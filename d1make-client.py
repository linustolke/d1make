#!/usr/bin/env python

import os
import select
import sys
import tempfile
import time

from FIFOServerThread import FIFOServerThread

"""The script is started with the following parameters:
* FIFO location
* Directory
* Command.
"""
def main():
    location = sys.argv[1]
    directory = sys.argv[2]
    command = sys.argv[3:]

    n1 = tempfile.mktemp()
    os.mkfifo(n1)

    n2 = tempfile.mktemp()
    os.mkfifo(n2)

    FIFOServerThread(location=location).send("compile",
                                             (n1, n2, directory, " ".join(command),))

    rl = dict()
    rl[os.open(n1, os.O_RDONLY)] = sys.stdout
    rl[os.open(n2, os.O_RDONLY)] = sys.stderr

    while rl:
        s = select.select(list(rl), [], [])
        for r in s[0]:
            red = os.read(r, 100)
            if not red:
                os.close(r)
                rl.pop(r)
                continue
            rl[r].write(red)
    os.remove(n1)
    os.remove(n2)

            
if __name__ == "__main__":
    main()
