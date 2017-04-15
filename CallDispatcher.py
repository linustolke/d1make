class CallDispatcher(object):
    def call(self, command, args):
        getattr(self, "call_" + command)(*args)
