import contextlib
import warnings

from resettabletimer import ResettableTimer


class PingManagerMixin:

    @property
    def __function(self):
        return self.wrapped_function

    @__function.setter
    def __function(self, value):
        self.function = value

    def wrapped_function(self, *args, **kwargs):
        self.function(*args, **kwargs)
        self.reset()

    @contextlib.contextmanager
    def update_ping_deadline(self):
        yield
        self.reset()

    def should_ping(self):
        warnings.warn('Deprecated. Removing in v2.0.0.', DeprecationWarning)


class PingManager(PingManagerMixin, ResettableTimer):
    pass
