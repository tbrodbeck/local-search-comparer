"""Contains a simple implementation of a traceable list."""

class ListVar(object):
    """
    A traceable list. Has getter and setter methods and can register a callback method
    that gets called whenever a new value is set.
    """

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
