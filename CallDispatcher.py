class CallDispatcher(object):
    def call(command, args):
        getattr(self, "call_" + command)(*args)
