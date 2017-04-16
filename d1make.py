#!/usr/bin/env python

import os
import pexpect
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
        self.count = count
        self.min1 = min1
        self.min5 = min5
        self.min15 = min15

    def __str__(self):
        return self.host + "/" + self.fifo


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

    def new_info(self, hostinfo):
        print "NEW INFO:", hostinfo
        self.hosts[hostinfo.host] = hostinfo

    def host_closed(self, host):
        self.hosts.pop(host)

    def call_host(self, response_fifo):
        print "Dispatching for", self.hardwired
        r = FIFOServerThread(location=response_fifo)
        r.send("use_host", (self.hardwired,))
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
