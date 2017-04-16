#!/usr/bin/env python

import subprocess
import threading
import time

from FIFOServerThread import FIFOServerThread
from CallDispatcher import CallDispatcher


class ExecuteThread(threading.Thread):
    def init(self, stdout_fifo, stderr_fifo, directory, command):
        threading.Thread.__init__(self)
        self.stdout_fifo = stdout_fifo
        self.stderr_fifo = stderr_fifo
        self.directory = directory
        self.command = command

    def run(self):
        stdout_fd = os.open(self.stdout_fifo, os.O_WRONLY)
        stderr_fd = os.open(self.stderr_fifo, os.O_WRONLY)
        subprocess.Popen("cd " + self.directory + " && " + self.command,
                         shell=True,
                         stdout=stdout_fd,
                         stderr=stderr_fd).communicate()
        os.close(stdout_fd)
        os.close(stderr_fd)


class ServerMakeStarter(CallDispatcher, FIFOServerThread):
    def __init__(self):
        FIFOServerThread.__init__(self)
        self.running_threads = set()

    def call_compile(self, stdout_fifo, stderr_fifo, directory, command):
        t = ExecuteThread(stdout_fifo, stderr_fifo, directory, command).start()
        self.running_threads.add(t)

    def purge_finished(self):
        for t in self.running_threads:
            if not t.isAlive():
                self.running_threads.remove(t)

    def threads_left(self):
        self.purge_finished()
        return len(self.running_threads)


def main():
    sms = ServerMakeStarter()
    try:
        sms.start()
        while True:
            print sms.fifo, "RUNNING", sms.threads_left()
            time.sleep(10)
    finally:
        sms.close()


if __name__ == "__main__":
    main()
