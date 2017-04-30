#!/usr/bin/env python

import heapq
import logging
import os
import random
import re
import select
import subprocess
import sys
import tempfile
import threading
import time

from subprocess import Popen, PIPE
from FIFOServerThread import FIFOServerThread, FIFOClient
from CallDispatcher import CallDispatcher


class HostInfo(object):
    def __init__(self, host, fifo, count, min1, min5, min15):
        self.host = host
        self.fifo = fifo
        self.count = int(count)
        self.min1 = float(min1)
        self.min5 = float(min5)
        self.min15 = float(min15)
        self.started = 0

    def __str__(self):
        return (self.host + " " + self.fifo + " " 
                + str(self.count + self.started))

    def add_one(self):
        self.started = self.started + 1

    def value(self):
        return (self.count + self.min1 + self.min5 + self.min15
                + 4 * self.started)

    def __lt__(self, other):
        return self.value() < other.value()


class SSHServerConnection(threading.Thread):
    def __init__(self, host, register, ssh_ctl_path):
        threading.Thread.__init__(self)
        self.host = host
        self.register = register
        self.ssh_ctl_path = ssh_ctl_path
        self.setDaemon(True)
        self.process = None

    def run(self):
        command = [
            "ssh",
            "-M", "-S", self.ssh_ctl_path,
        ]
        extra_ssh_parameters = os.getenv("D1MAKE_EXTRA_SSH_PARAMETERS", None)
        if extra_ssh_parameters:
            command.extend(extra_ssh_parameters.split(" "))
        command.append(self.host)
        server_setup = os.getenv("D1MAKE_SERVER_SETUP", None)
        if server_setup:
            command.append(server_setup)
        command.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "d1make-server.py"))
        logging.debug("Starting command=" + " ".join(command))
        self.process = subprocess.Popen(command,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
        	                        stderr=subprocess.STDOUT)
        try:
            self.process.stdin.close()
            while True:
                line = self.process.stdout.readline().rstrip()
                logging.debug("Read from " + self.host + ": " + line)
                if line:
                    fifo, _, count, min1, min5, min15 = line.strip().split(" ")
                    self.register.new_info(HostInfo(self.host, fifo, count,
                                                    min1, min5, min15))
                else:
                    break
        except ValueError:
            logging.error("Strange data from " + self.host + ": " + line)
            self.register.host_closed(self.host)
            self.process.terminate()
            for line in self.process.stdout.readlines():
                logging.error("Strange data from " + self.host + ": " + line)
        finally:
            self.process.kill()
        self.register.host_closed(self.host)

    def close(self):
        if self.process:
            self.process.terminate()

    def collect(self):
        self.join(1)


class AnswerWithHost(CallDispatcher, FIFOServerThread):
    def __init__(self):
        FIFOServerThread.__init__(self)
        self.hosts = []
        self.hosts_lock = threading.Lock()

    def new_info(self, hostinfo):
        logging.info("New info from " + str(hostinfo))
        self.hosts_lock.acquire()
        try:
            for i, info in enumerate(self.hosts):
                if info.host == hostinfo.host:
                    self.hosts[i] = hostinfo
                    heapq.heapify(self.hosts)
                    return
            heapq.heappush(self.hosts, hostinfo)
        finally:
            self.hosts_lock.release()

    def host_closed(self, host):
        self.hosts_lock.acquire()
        try:
            for i, info in enumerate(self.hosts):
                if info.host == host:
                    self.hosts[i] = self.hosts[-1]
                    self.hosts.pop()
                    heapq.heapify(self.hosts)
                    break
        finally:
            self.hosts_lock.release()
                
    def calculate_host(self):
        while True:
            self.hosts_lock.acquire()
            try:
                if not self.hosts:
                    logging.info("No hosts are available.")
                else:
                    info = heapq.heappop(self.hosts)
                    info.add_one()
                    heapq.heappush(self.hosts, info)
                    return info
            finally:
                self.hosts_lock.release()
            time.sleep(1)

    def call_host(self, response_fifo):
        hostinfo = self.calculate_host()
        logging.info("Start job for " + str(hostinfo))
        r = FIFOClient(location=response_fifo)
        r.send("use_host", (hostinfo.host, hostinfo.fifo,))
        r.close()


def main():
    logging.basicConfig(level=logging.INFO)
    hostnames = os.getenv("D1MAKE_HOSTS").split(" ")
    a = AnswerWithHost()
    hosts = dict()
    ssh_ctl_path_root = tempfile.mktemp("-%n-%h", "ssh_ctl_path-")
    for host in hostnames:
        ssc = SSHServerConnection(host, a, ssh_ctl_path_root)
        hosts[host] = ssc
        ssc.start()
    a.start()
    p = Popen(["make", "-f", "-"] + sys.argv[1:], stdin=PIPE)
    makefile = open("makefile", "r").read()
    client_program = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "d1make-client.py")
    new_makefile = re.subn(r"(\n\t.* )(make|\$\(MAKE\)|\$\(sub-make\)) ",
                           r"\1" + client_program + " "
                           + a.fifo + " "
                           + ssh_ctl_path_root + " "
                           + "make "
                           + os.getenv("D1MAKE_CLIENT_MAKEARGS", "") + " ",
                           makefile)[0]
    p.communicate(input=new_makefile)
    a.stop()
    for ssc in hosts.values():
        ssc.close()
    for ssc in hosts.values():
        ssc.collect()
    sys.exit(p.returncode)


if __name__ == '__main__':
    main()
