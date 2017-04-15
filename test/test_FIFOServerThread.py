import unittest

from FIFOServerThread import FIFOServerThread


class test_FIFOServerThread(unittest.TestCase):
    def test_open_and_close(self):
        FIFOServerThread().close()

    def test_open_start_and_close(self):
        t = FIFOServerThread()
        t.start()
        t.close()

    def test_fail_when_not_initialized(self):
        try:
            FIFOServerThread().send("command", [])
            self.fail("Should have failed")
        except OSError:
            pass


if __name__ == "__main__":
    unittest.main()
