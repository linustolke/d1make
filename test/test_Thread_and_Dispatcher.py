"""A test to learn how the FIFOServerThread and CallDispatcher works together.
"""

import time
import unittest

from FIFOServerThread import FIFOServerThread
from CallDispatcher import CallDispatcher



class ThreadAndDispatcherMock(CallDispatcher, FIFOServerThread):
    def call_zero(self):
        self.zero = True

    def call_one(self, arg1):
        self.one = True
        self.arg1 = arg1

    def call_two(self, arg1, arg2):
        self.two = True
        self.arg1 = arg1
        self.arg2 = arg2


class test_Thread_and_Dispatcher(unittest.TestCase):
    def test_call_zero(self):
        t = ThreadAndDispatcherMock()
        t.start()
        t.send("zero", [])
        time.sleep(0.2)
        t.close()
        self.assertTrue(t.zero)

    def test_call_one(self):
        t = ThreadAndDispatcherMock()
        t.start()
        t.send("one", ("uno",))
        time.sleep(0.2)
        t.close()
        self.assertTrue(t.one)
        self.assertEqual(t.arg1, "uno")

    def test_call_two(self):
        t = ThreadAndDispatcherMock()
        t.start()
        t.send("two", ("uno", 2,))
        time.sleep(0.2)
        t.close()
        self.assertTrue(t.two)
        self.assertEqual(t.arg1, "uno")
        self.assertEqual(t.arg2, 2)
