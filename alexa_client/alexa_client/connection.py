import json
import http

from requests_toolbelt import MultipartEncoder
from requests.exceptions import HTTPError
from hyper import HTTP20Connection

from alexa_client.alexa_client import helpers


class ConnectionManager:
    host = 'avs-alexa-eu.amazon.com'
    connection = None

    def create_connection(self):
        self.connection = HTTP20Connection(
            host=self.host, secure=True, force_proto='h2',
        )

    def establish_downchannel_stream(self, authentication_headers):
        self.connection.request(
            'GET',
            '/v20160207/directives',
            headers=authentication_headers
        )

    def synchronise_device_state(self, device_state, authentication_headers):
        """
        Synchronizing the component states with AVS

        Components state must be synchronised with AVS after establishing the
        downchannel stream in order to create a persistent connection with AVS.

        Note that currently this function is paying lip-service synchronising
        the device state: the device state is hard-coded.

        """

        payload = {
            'context': device_state,
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
            **authentication_headers,
            'Content-Type': multipart_data.content_type
        }
        stream_id = self.connection.request(
            'POST',
            '/v20160207/events',
            body=multipart_data,
            headers=headers,
        )
        response = self.connection.get_response(stream_id)
        assert response.status == http.client.NO_CONTENT

    def send_audio_file(
        self, audio_file, device_state, authentication_headers,
        dialog_request_id, distance_profile, audio_format
    ):
        """
        Send audio to AVS

        The file-like object are steaming uploaded for improved latency.

        Returns:
            bytes -- wav audio bytes returned from AVS

        """

        payload = {
            'context': device_state,
            'event': {
                'header': {
                    'namespace': 'SpeechRecognizer',
                    'name': 'Recognize',
                    'messageId': self.generate_message_id(),
                    'dialogRequestId': dialog_request_id,
                },
                'payload': {
                    'profile': distance_profile,
                    'format': audio_format
                }
            }
        }
        multipart_data = MultipartEncoder(
            fields=[
                (
                    'request', (
                        'request',
                        json.dumps(payload),
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
            **authentication_headers,
            'Content-Type': multipart_data.content_type
        }
        stream_id = self.connection.request(
            'POST',
            '/v20160207/events',
            headers=headers,
            body=multipart_data,
        )
        response = self.connection.get_response(stream_id)
        return self.parse_response(response)

    def ping(self, authentication_headers):
        stream_id = self.connection.request(
            'GET',
            '/ping',
            headers=authentication_headers,
        )
        return self.connection.get_response(stream_id)

    @staticmethod
    def parse_response(response):
        if response.status == http.client.NO_CONTENT:
            return None
        if not response.status == http.client.OK:
            raise HTTPError(response=response)
        return helpers.AVSMultipartDecoder(response).directives

    @staticmethod
    def generate_message_id():
        return helpers.generate_unique_id()
