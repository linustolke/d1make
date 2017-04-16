import os
import select
import sys
import tempfile
import time

from FIFOServerThread import FIFOServerThread


def main():
    n1 = tempfile.mktemp()
    f1 = os.mkfifo(n1)

    n2 = tempfile.mktemp()
    f2 = os.mkfifo(n2)

    FIFOServerThread(location=sys.argv[1]).send("compile",
                                                (n1, n2, "/tmp", "sleep 10",))

    rl = [
        os.open(f1, os.O_RDONLY),
        os.open(f2, os.O_RDONLY),
    ]

    while rl:
        s = select.select([r1, r2], [], [])
        for r in s[0]:
            red = os.read(r)
            if not red:
                rl.remove(r)

            
if __name__ == "__main__":
    main()
