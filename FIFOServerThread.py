import ast
import os
import tempfile
import threading


class FIFOServerThread(threading.Thread):
    """Base class for sending and receiving commands from a FIFO."""
    def __init__(self, chunk_size=1000, location=None):
        threading.Thread.__init__(self)
        self.chunk_size = chunk_size
        assert self.chunk_size <= 16 * 1024
        self.write_fd = None
        if location:
            self.fifo = location
        else:
            self.fifo = tempfile.mktemp()

    def start(self):
        """Create a thread listening to a FIFO.

        For sending clients, this shall not be called."""
        os.mkfifo(self.fifo)
        threading.Thread.start(self)

    def run(self):
        fifo = self.fifo
        try:
            fd = os.open(self.fifo, os.O_RDONLY)
            while True:
                red = os.read(fd, self.chunk_size)
                if len(red) == 0:
                    break
                if len(red) != self.chunk_size:
                    raise IllegalArgumentException("Garbage read")
                command, args = self.unpack(red)
                if (command == "close"
                        and len(args) == 1
                        and args[0] == self.fifo):
                    self.fifo = None
                    break
                self.call(command, args)
        finally:
            os.close(fd)
            os.remove(fifo)

    def unpack(self, data_chunk):
        command, args = ast.literal_eval(data_chunk)
        return command, args

    def call(self, command, args):
        raise NotImplementedError("In base class")

    def pack(self, command, args):
        s = str((command, args,))
        if len(s) > self.chunk_size:
            raise IllegalArgumentException("Too big data chunk")
        out = s + " " * (self.chunk_size - len(s))
        assert len(out) == self.chunk_size
        return out

    def send(self, command, args):
        if not self.write_fd:
            self.write_fd = os.open(self.fifo, os.O_WRONLY)
        l = os.write(self.write_fd, self.pack(command, args))
        assert l == self.chunk_size

    def close(self):
        if self.fifo and os.path.exists(self.fifo):
            self.send("close", (self.fifo,))
        if self.write_fd:
            os.close(self.write_fd)
            self.write_fd = None
