#!/usr/bin/env python

import os
import select
import sys
import tempfile
import time
from subprocess import Popen

from FIFOServerThread import FIFOServerThread
from CallDispatcher import CallDispatcher

"""The script is started with the following parameters:
* FIFO location, where to get the ssh host,
  or "LOCAL" if already on the remote side of the ssh connection
  i.e. no new ssh connection to create.
* FIFO location, on the host
* Directory
* Command.
"""

def run_command_locally(location, directory, command):
    global exit_code

    n1 = tempfile.mktemp()
    os.mkfifo(n1)

    n2 = tempfile.mktemp()
    os.mkfifo(n2)

    n3 = tempfile.mktemp()
    os.mkfifo(n3)

    FIFOServerThread(location=location).send("compile",
                                             (n1, n2, n3, directory, " ".join(command),))

    rl = dict()
    rl[os.open(n1, os.O_RDONLY)] = sys.stdout
    rl[os.open(n2, os.O_RDONLY)] = sys.stderr
    rl[os.open(n3, os.O_RDONLY)] = "EXIT_CODE"

    while rl:
        s = select.select(list(rl), [], [])
        for r in s[0]:
            red = os.read(r, 100)
            if not red:
                os.close(r)
                rl.pop(r)
                continue
            if rl[r] == "EXIT_CODE":
                exit_code = int(red)
            else:
                rl[r].write(red)
    os.remove(n1)
    os.remove(n2)


class SSHThread(CallDispatcher, FIFOServerThread):
    def __init__(self, location, directory, command):
        FIFOServerThread.__init__(self)
        self.location = location
        self.directory = directory
        self.command = command

    def call_use_host(self, host):
        p = Popen(["ssh", host,
                   __file__, "LOCAL", self.location, self.directory] + self.command)
        p.communicate()
        self.exit_code = p.wait()
        self.stop()


def main():
    global exit_code

    sshlocation = sys.argv[1]
    location = sys.argv[2]
    directory = sys.argv[3]
    command = sys.argv[4:]

    if sshlocation == "LOCAL":
        run_command_locally(location, directory, command)
        sys.exit(exit_code)
    else:
        master = FIFOServerThread(location=sshlocation)
        response = SSHThread(location, directory, command)
        response.start()
        master.send("host", (response.fifo,))
        response.join()
        sys.exit(response.exit_code)

            
if __name__ == "__main__":
    main()
