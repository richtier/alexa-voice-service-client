import warnings

from alexa_client.alexa_client import (
    authentication, connection, constants, device, helpers, ping
)


class AlexaClient:
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
        self.ping_manager = self.ping_manager_class(60*4, self.ping)

    def connect(self):
        self.authentication_manager.prefetch_api_token()
        self.connection_manager.create_connection()
        self.establish_downchannel_stream()
        self.synchronise_device_state()
        self.ping_manager.start()

    def conditional_ping(self):
        warnings.warn('Deprecated. Removing in v2.0.0.', DeprecationWarning)

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

    def send_audio_file(
        self, audio_file, dialog_request_id=None,
        distance_profile=constants.CLOSE_TALK, audio_format=constants.PCM
    ):
        dialog_request_id = dialog_request_id or helpers.generate_unique_id()
        with self.ping_manager.update_ping_deadline():
            headers = self.authentication_manager.get_headers()
            return self.connection_manager.send_audio_file(
                authentication_headers=headers,
                device_state=self.device_manager.get_device_state(),
                audio_file=audio_file,
                dialog_request_id=dialog_request_id,
                distance_profile=distance_profile,
                audio_format=audio_format,
            )

    def ping(self):
        headers = self.authentication_manager.get_headers()
        return self.connection_manager.ping(
            authentication_headers=headers,
        )


class AlexaVoiceServiceClient(AlexaClient):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            'Deprecated. Use AlexaClient. Removing in v2.0.0.',
            DeprecationWarning
        )
        super().__init__(*args, **kwargs)
