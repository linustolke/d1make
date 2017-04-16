#!/usr/bin/env python

import os
import pexpect
import random
import select
import sys
import tempfile
import threading
import time

from FIFOServerThread import FIFOServerThread
from CallDispatcher import CallDispatcher


class HostInfo(object):
    def __init__(self, host, fifo, count, min1, min5, min15):
        self.host = host
        self.fifo = fifo
        self.count = int(count)
        self.min1 = float(min1)
        self.min5 = float(min5)
        self.min15 = float(min15)

    def __str__(self):
        return self.host + "/" + self.fifo

    def weight(self):
        return 1 / (1 + self.count + self.min1 + self.min5 + self.min15)


class SSHServerConnection(threading.Thread):
    def __init__(self, host, register):
        threading.Thread.__init__(self)
        self.host = host
        self.register = register
        self.setDaemon(True)

    def run(self):
        p = pexpect.spawn("ssh " + self.host + " "
                          + os.path.join(
                              os.path.dirname(os.path.abspath(__file__)),
                              "d1make-server.py"))
        try:
            while True:
                line = p.readline()
                if line:
                    fifo, _, count, min1, min5, min15 = line.strip().split(" ")
                    self.register.new_info(HostInfo(self.host, fifo, count,
                                                    min1, min5, min15))
                else:
                    break
        except ValueError:
            self.register.host_closed(self.host)
            p.terminate()
            for line in p.readlines():
                print "Strange data from", self.host, line
        finally:
            p.terminate(force=True)


class AnswerWithHost(CallDispatcher, FIFOServerThread):
    def __init__(self):
        FIFOServerThread.__init__(self)
        self.hardwired = "localhost"
        self.hosts = dict()
        self.random = random.Random()

    def new_info(self, hostinfo):
        print "NEW INFO:", hostinfo
        self.hosts[hostinfo.host] = hostinfo

    def host_closed(self, host):
        self.hosts.pop(host)

    def calculate_host(self):
        while not self.hosts:
            print "No hosts are available."
            time.sleep(1)
        weighted_array = list()
        for host in self.hosts:
            weighted_array.extend([host] * int(1000 * self.hosts[host].weight()))
        return self.random.sample(weighted_array, 1)[0]

    def call_host(self, response_fifo):
        host = self.calculate_host()
        print "Dispatching for", host
        r = FIFOServerThread(location=response_fifo)
        r.send("use_host", (host, self.hosts[host].fifo,))
        r.close()
        print "Dispatched."


def main():
    hostnames = os.getenv("D1MAKE_HOSTS").split(" ")
    a = AnswerWithHost()
    hosts = dict()
    for host in hostnames:
        ssc = SSHServerConnection(host, a)
        hosts[host] = ssc
        ssc.start()
    a.start()
    print a.fifo
    time.sleep(100)
    a.stop()


if __name__ == '__main__':
    main()
