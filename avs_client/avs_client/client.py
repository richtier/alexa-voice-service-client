from functools import wraps

from hyper.http20.exceptions import StreamResetError

from avs_client.avs_client import authentication, connection, device, ping


class AlexaVoiceServiceClient:
    authentication_manager_class = (
        authentication.AlexaVoiceServiceTokenAuthenticator
    )
    device_manager_class = device.DeviceManager
    connection_manager_class = connection.ConnectionManager
    ping_manager_class = ping.PingManager

    ping_manager = None
    authentication_manager = None
    connection_manager = None
    device_manager = None

    def __init__(self, client_id, secret, refresh_token):
        self.authentication_manager = self.authentication_manager_class(
            client_id=client_id, secret=secret, refresh_token=refresh_token,
        )
        self.device_manager = self.device_manager_class()
        self.connection_manager = self.connection_manager_class()
        self.ping_manager = self.ping_manager_class()

    def retry_once_on_stream_reset(f):
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except StreamResetError:
                self.connect()
                return f(self, *args, **kwargs)
        return wrapped

    def connect(self):
        self.authentication_manager.prefetch_api_token()
        self.connection_manager.create_connection()
        self.establish_downchannel_stream()
        self.synchronise_device_state()

    def establish_downchannel_stream(self):
        return self.connection_manager.establish_downchannel_stream(
            authentication_headers=self.authentication_manager.get_headers(),
        )

    def synchronise_device_state(self):
        with self.ping_manager.update_ping_deadline():
            headers = self.authentication_manager.get_headers()
            return self.connection_manager.synchronise_device_state(
                authentication_headers=headers,
                device_state=self.device_manager.get_device_state(),
            )

    def send_audio_file(self, audio_file) -> bytes:
        with self.ping_manager.update_ping_deadline():
            headers = self.authentication_manager.get_headers()
            return self.connection_manager.send_audio_file(
                authentication_headers=headers,
                device_state=self.device_manager.get_device_state(),
                audio_file=audio_file,
            )

    @retry_once_on_stream_reset
    def conditional_ping(self):
        if self.ping_manager.should_ping():
            with self.ping_manager.update_ping_deadline():
                headers = self.authentication_manager.get_headers()
                return self.connection_manager.ping(
                    authentication_headers=headers,
                )
