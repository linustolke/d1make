#!/usr/bin/env python

"""The script is started either as a replacement for make (before ssh)
or as a remote client that relays the work (after ssh).

As the first, the parameters are:
* FIFO location, where to get the ssh host,
* SSH Control Path
* Command

As the second, the parameters are:
* "--remote"
* FIFO location, to contact the remote server
* Directory
* Command.
"""

import os
import select
import sys
import tempfile
from subprocess import Popen, PIPE

from FIFOServerThread import FIFOServerThread, FIFOClient
from CallDispatcher import CallDispatcher


def run_command_locally(location, directory, command):
    n1 = tempfile.mktemp()
    os.mkfifo(n1)

    n2 = tempfile.mktemp()
    os.mkfifo(n2)

    n3 = tempfile.mktemp()
    os.mkfifo(n3)

    c = FIFOClient(location=location)
    c.send("compile", (n1, n2, n3, directory, " ".join(command),))

    rl = dict()
    rl[os.open(n1, os.O_RDONLY)] = sys.stdout
    rl[os.open(n2, os.O_RDONLY)] = sys.stderr
    rl[os.open(n3, os.O_RDONLY)] = "EXIT_CODE"

    c.close()

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
                rl[r].flush()
    os.remove(n1)
    os.remove(n2)
    os.remove(n3)
    return exit_code


class SSHThread(CallDispatcher, FIFOServerThread):
    def __init__(self, directory, ssh_ctl_path, command):
        FIFOServerThread.__init__(self)
        self.directory = directory
        self.ssh_ctl_path = ssh_ctl_path
        self.command = command

    def call_use_host(self, host, fifolocation):
        ssh_parameters = []
        ssh_parameters.extend(["-S", self.ssh_ctl_path])
        extra_parameters = os.getenv("D1MAKE_EXTRA_SSH_PARAMETERS", None)
        if extra_parameters:
            ssh_parameters.extend(extra_parameters.split(" "))
        ssh_parameters.append(host)
        ssh_parameters.append(os.path.abspath(__file__))
        ssh_parameters.extend(["--remote", fifolocation, self.directory])
        p = Popen(["ssh"]
                  + ssh_parameters
                  + self.command,
                  stdin=PIPE)
        p.communicate()
        self.exit_code = p.wait()
        self.send_close()


def main():
    if sys.argv[1] == "--remote":
        exit_code = run_command_locally(sys.argv[2], sys.argv[3], sys.argv[4:])
        sys.exit(exit_code)
    else:
        master = FIFOClient(location=sys.argv[1])
        response = SSHThread(os.getcwd(), sys.argv[2], sys.argv[3:])
        response.start()
        master.send("host", (response.fifo,))
        master.close()
        response.join()
        sys.exit(response.exit_code)

            
if __name__ == "__main__":
    main()
