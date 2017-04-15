import unittest

from CallDispatcher import CallDispatcher

class CDSpecialization(CallDispatcher):
    def call_test_0(self):
        pass

    def call_test_1(self):
        pass

class test_CallDispatcher(unittest.TestCase):
    def test_zero_args(self):
        cd = CDSpecialization()
        cd.call("test_0", [])
