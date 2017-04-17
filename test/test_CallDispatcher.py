import unittest

from CallDispatcher import CallDispatcher


class CDSpecialization(CallDispatcher):
    def __init__(self, callback):
        self.callback = callback

    def call_test_0(self):
        self.callback.callback((0,))

    def call_test_1(self, arg1):
        self.callback.callback((1, arg1,))

    def call_test_2(self, arg1, arg2):
        self.callback.callback((1, arg1, arg2,))


class test_CallDispatcher(unittest.TestCase):
    def callback(self, t):
        self.received = t

    def test_zero_args(self):
        cd = CDSpecialization(self)
        cd.call("test_0", [])
        self.assertEqual(self.received, (0,))

    def test_one_arg(self):
        cd = CDSpecialization(self)
        cd.call("test_1", ("string",))
        self.assertEqual(self.received, (1, "string",))

    def test_two_args(self):
        cd = CDSpecialization(self)
        cd.call("test_2", ("string", 17,))
        self.assertEqual(self.received, (1, "string", 17,))


if __name__ == "__main__":
    unittest.main()
