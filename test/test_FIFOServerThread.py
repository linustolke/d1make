import time
import unittest

from FIFOServerThread import FIFOServerThread


class CommandMock(FIFOServerThread):
    def call(self, command, args):
        self.command = command
        self.args = args

class test_FIFOServerThread(unittest.TestCase):
    def test_open_and_close(self):
        FIFOServerThread().close()

    def test_open_start_and_close(self):
        t = FIFOServerThread()
        t.start()
        t.close()

    def test_fail_when_not_started(self):
        try:
            FIFOServerThread().send("command", [])
            self.fail("Should have failed")
        except OSError:
            pass

    def test_receive_command(self):
        t = CommandMock()
        t.start()
        t.send("gupta", ("trade", 17,))
        time.sleep(0.2)
        self.assertEqual(t.command, "gupta")
        self.assertEqual(t.args, ("trade", 17,))
        t.close()


if __name__ == "__main__":
    unittest.main()
