class CallDispatcher(object):
    """Dispatches a call to the correct method.

    The intention of this class is to use it together with
    FIFOServerThread.  Since FIFOServerThread also implements the call
    method and the intention is that the call method in this class is
    supposed to override the call method from the FIFOServerThread the
    order specifying the two classes is significant. Specify this
    class first.

    class MyClass(CallDispatcher, FIFOServerThread):
        def call_mycommand(self, ...):
            ...
    """
    def call(self, command, args):
        getattr(self, "call_" + command)(*args)
