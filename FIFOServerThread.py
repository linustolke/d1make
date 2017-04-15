import os
import tempfile
import threading


class FIFOServerThread(threading.Thread):
    """Base class for sending and receiving commands from a FIFO."""
    def __init__(self, chunk_size=1000, location=None):
        threading.Thread.__init__()
        self.chunk_size = chunk_size
        assert self.chunk_size <= 16 * 1024
        if location:
            self.fifo = location
        else:
            self.fifo = tempfile.mktemp()

    def start(self):
        os.mkfifo(self.fifo)
        threading.Thread.start()

    def run(self):
        try:
            fd = os.open(self.fifo, os.O_RDONLY)
            while True:
                red = os.read(fd, self.chunk_size)
                if len(red) == 0:
                    break
                if len(red) != self.chunk_size:
                    raise IllegalArgumentException("Garbage read")
                self.process(red)
        finally:
            os.close(fd)

