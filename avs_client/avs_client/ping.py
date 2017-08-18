import contextlib
from datetime import datetime, timedelta


class PingManager:
    ping_deadline = None
    delta = timedelta(seconds=60*4)

    @contextlib.contextmanager
    def update_ping_deadline(self):
        """
        Updates time when ping should be called.
        
        The client must send a PING frame to AVS every five minutes when the
        connection is idle. Failure to do so will result in a closed
        connection.
        
        """
        yield
        self.ping_deadline = datetime.utcnow() + self.delta

    def should_ping(self):
        return (
            self.ping_deadline is not None and
            datetime.utcnow() >= self.ping_deadline
        )
