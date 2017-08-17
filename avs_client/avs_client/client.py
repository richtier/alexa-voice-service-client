from avs_client.avs_client import authentication, connection, device, ping


class AlexaVoiceServiceClient:
    authentication_class = authentication.AlexaVoiceServiceTokenAuthenticator
    device_manager_class = device.DeviceManager
    connection_manager_class = connection.ConnectionManager
    ping_manager_class = ping.PingManager

    ping_manager = None
    authenticator = None
    connection_manager = None
    device_manager = None

    def __init__(self, client_id, secret, refresh_token):
        self.authenticator = self.authentication_class(
            client_id=client_id, secret=secret, refresh_token=refresh_token,
        )
        self.device_manager = self.device_manager_class()
        self.connection_manager = self.connection_manager_class()
        self.ping_manager = self.ping_manager_class()

    def connect(self):
        self.authenticator.prefetch_api_token()
        self.establish_downchannel_stream()
        self.synchronise_device_state()

    def establish_downchannel_stream(self):
        return self.connection_manager.establish_downchannel_stream(
            authentication_headers=self.authenticator.get_headers(),
        )

    def synchronise_device_state(self):
        with self.ping_manager.update_ping_deadline():
            return self.connection_manager.synchronise_device_state(
                device_state=self.device_manager.get_device_state(),
                authentication_headers=self.authenticator.get_headers(),
            )

    def send_audio_file(self, audio_file) -> bytes:
        with self.ping_manager.update_ping_deadline():
            return self.connection_manager.send_audio_file(
                audio_file=audio_file,
                device_state=self.device_manager.get_device_state(),
                authentication_headers=self.authenticator.get_headers(),
            )

    def conditional_ping(self):
        if self.ping_manager.should_ping():
            with self.ping_manager.update_ping_deadline():
                return self.connection_manager.ping()
