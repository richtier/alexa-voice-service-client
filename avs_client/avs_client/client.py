from datetime import datetime, timedelta
import json
import http
import typing
import uuid

from requests_toolbelt import MultipartDecoder, MultipartEncoder
from requests.exceptions import HTTPError
from hyper import HTTP20Connection

from avs_client import authentication, device


class AlexaVoiceServiceClient:

    host = 'avs-alexa-eu.amazon.com'
    authentication_class = authentication.AlexaVoiceServiceTokenAuthenticator
    device_manager_class = device.DeviceManager
    connection = None
    ping_deadline = None

    def __init__(self, client_id, secret, refresh_token):
        self.authenticator = self.authentication_class(
            client_id=client_id, secret=secret, refresh_token=refresh_token,
        )
        self.device_manager = self.device_manager_class()
        self.connection = HTTP20Connection(host=self.host, secure=True)

    def connect(self):
        self.authenticator.prefetch_api_token()
        self.establish_downchannel_stream()
        self.synchronise_device_state()

    def establish_downchannel_stream(self):
        self.connection.request(
            'GET',
            '/v20160207/directives',
            headers=self.get_headers()
        )

    def synchronise_device_state(self):
        """
        Synchronizing the component states with AVS

        Components state must be synchronised with AVS after establishing the
        downchannel stream in order to create a persistent connection with AVS.

        Note that currently this function is paying lip-service synchronising
        the device state: the device state is hard-coded.

        """

        payload = {
            'context': self.device_manager.get_device_state(),
            'event': {
                'header': {
                    'namespace': 'System',
                    'name': 'SynchronizeState',
                    'messageId': ''
                },
                'payload': {}
            }
        }
        multipart_data = MultipartEncoder(
            fields=[
                (
                    'metadata', (
                        'metadata',
                        json.dumps(payload),
                        'application/json',
                        {'Content-Disposition': "form-data; name='metadata'"}
                    )
                ),
            ],
            boundary='boundary'
        )
        headers = {
            **self.get_headers(),
            'Content-Type': multipart_data.content_type
        }
        stream_id = self.connection.request(
            'GET',
            '/v20160207/events',
            body=multipart_data,
            headers=headers,
        )
        response = self.connection.get_response(stream_id)
        assert response.status == http.client.NO_CONTENT

    def get_request_data(self) -> dict:
        return {
            'context': self.device_manager.get_device_state(),
            'event': {
                'header': {
                    'namespace': 'SpeechRecognizer',
                    'name': 'Recognize',
                    'messageId': self.generate_message_id(),
                    'dialogRequestId': self.generate_dialogue_id(),
                },
                'payload': {
                    'profile': 'CLOSE_TALK',
                    'format': 'AUDIO_L16_RATE_16000_CHANNELS_1'
                }
            }
        }

    def send_audio_file(self, audio_file) -> bytes:
        """
        Send audio to AVS
        
        The file-like object are steaming uploaded for improved latency.
        
        Returns:
            bytes -- wav audio bytes returned from AVS

        """

        multipart_data = MultipartEncoder(
            fields=[
                (
                    'request', (
                        'request',
                        json.dumps(self.get_request_data()),
                        'application/json;',
                        {'Content-Disposition': "form-data; name='request'"}
                    ),
                ),
                (
                    'audio', (
                        'audio',
                        audio_file,
                        'application/octet-stream',
                        {'Content-Disposition': "form-data; name='audio'"}
                    )
                ),
            ],
            boundary='boundary',
        )
        headers = {
            **self.get_headers(),
            'Content-Type': multipart_data.content_type
        }
        stream_id = self.connection.request(
            'POST',
            '/v20160207/events',
            headers=headers,
            body=multipart_data,
        )
        self.update_ping_deadline()
        response = self.connection.get_response(stream_id)
        return self.parse_response(response)

    @staticmethod
    def parse_response(response) -> typing.Union[bytes, None]:
        if response.status == 204:
            return None
        if not response.status == 200:
            raise HTTPError(response=response)

        parsed = MultipartDecoder(
            response.read(),
            response.headers['content-type'][0].decode()
        )
        for part in parsed.parts:
            if part.headers[b'Content-Type'] == b'application/octet-stream':
                return part.content

    def update_ping_deadline(self):
        """
        Updates time when ping should be called.
        
        The client must send a PING frame to AVS every five minutes when the
        connection is idle. Failure to do so will result in a closed
        connection.
        
        """

        self.ping_deadline = datetime.utcnow() + timedelta(seconds=60*4)

    def should_ping(self):
        return (
            self.ping_deadline is not None and
            datetime.utcnow() >= self.ping_deadline
        )

    def ping(self):
        self.connection.ping(b'********')

    @staticmethod
    def generate_dialogue_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def generate_message_id() -> str:
        return str(uuid.uuid4())

    def get_headers(self) -> dict:
        return self.authenticator.get_authentication_headers()
