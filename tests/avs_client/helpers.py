from io import BytesIO

from hpack.hpack_compat import Encoder
from hyperframe.frame import DataFrame, HeadersFrame
from requests_toolbelt import MultipartDecoder


class DummySocket:
    def __init__(self, buffer):
        self.queue = []
        self._buffer = buffer or BytesIO()
        self._read_counter = 0
        self.can_read = False

    @property
    def buffer(self):
        return memoryview(self._buffer.getvalue()[self._read_counter:])

    @buffer.setter
    def buffer(self, value):
        self._buffer = value
        self._read_counter = 0

    def advance_buffer(self, amt):
        self._read_counter += amt
        self._buffer.read(amt)

    def send(self, data):
        self.queue.append(data)

    sendall = send

    def recv(self, l):
        data = self._buffer.read(l)
        self._read_counter += len(data)
        return memoryview(data)

    def close(self):
        pass

    def fill(self):
        pass


class TestConnectionMixin:
    """
    Mixin for use with avs_client.client.AlexaVoiceServiceClient that
    creates a test double that mocks out non-deterministic methods and external
    services, and adds helper functions

    """

    def mock_response(self, *, status_code, data=b''):
        # test helper method
        self.connection._sock = self.create_socket(
            status_code=status_code, data=data,
        )

    @staticmethod
    def create_socket(status_code, data):
        # test helper method
        encoder = Encoder()
        h1 = HeadersFrame(1)
        h1.data = encoder.encode(
            [(':status', status_code), ('content-length', len(data))]
        )
        h1.flags |= set(['END_HEADERS'])

        d1 = DataFrame(1)
        d1.data = data

        d2 = DataFrame(1)
        d2.flags |= set(['END_STREAM'])

        content = b''.join(f.serialize() for f in [h1, d1, d2])
        buffer = BytesIO(content)

        return DummySocket(buffer)


def parse_multipart(body, content_type, boundary=b'--boundary'):
    # remove the frame header as that prevents parsing the multipart request
    # (generated in frame serialization)
    body = boundary.join(body.split(boundary)[1:])
    return MultipartDecoder(body, content_type)
