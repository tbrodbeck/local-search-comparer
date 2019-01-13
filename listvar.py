class ListVar(object):
    def __init__(self, length):
        self.data = [0] * length
        self.trace_callback = None

    def get(self):
        return self.data.copy()

    def set(self, value):
        self.data = value.copy()

        if self.trace_callback is not None:
            self.trace_callback()

    def trace(self, callback):
        self.trace_callback = callback
