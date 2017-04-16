#!/usr/bin/env python

import os
import select
import sys
import tempfile
import time

from FIFOServerThread import FIFOServerThread
from CallDispatcher import CallDispatcher


class AnswerWithHost(CallDispatcher, FIFOServerThread):
    def __init__(self):
        FIFOServerThread.__init__(self)
        self.hardwired = "localhost"

    def call_host(self, response_fifo):
        print "Dispatching for", self.hardwired
        r = FIFOServerThread(location=response_fifo)
        r.send("use_host", (self.hardwired,))
        r.close()
        print "Dispatched."


def main():
    a = AnswerWithHost()
    a.start()
    print a.fifo
    time.sleep(100)
    a.stop()


if __name__ == '__main__':
    main()
