from datetime import datetime
import json
from io import BytesIO
from unittest.mock import patch

from freezegun import freeze_time
import pytest
from requests.exceptions import HTTPError

from avs_client.client import AlexaVoiceServiceClient
from tests.avs_client.helpers import TestClientMixin, parse_multipart


class TestAlexaVoiceServiceClient(TestClientMixin, AlexaVoiceServiceClient):
    pass


@pytest.fixture
def audio_file():
    return BytesIO(b'things')


@pytest.fixture
def test_client():
    return TestAlexaVoiceServiceClient(
        client_id='test_client_id',
        secret='test_secret',
        refresh_token='test_refresh_token',
    )


@pytest.fixture
def client():
    return AlexaVoiceServiceClient(
        client_id='test_client_id',
        secret='test_secret',
        refresh_token='test_refresh_token',
    )


def test_create_connection_prefetches_api_token(test_client):
    assert test_client.connection.host == 'avs-alexa-eu.amazon.com'
    assert test_client.connection.secure is True


def test_establish_downchannel_stream(test_client):
    test_client.mock_response(status_code=200)
    test_client.establish_downchannel_stream()

    headers = dict(list(test_client.connection.recent_stream.headers.items()))

    assert headers == {
        b':scheme': b'https',
        b':method': b'GET',
        b':path': b'/v20160207/directives',
        b':authority': b'avs-alexa-eu.amazon.com',
        b'custom_header_one': b'value',
    }


def test_synchronise_device_state(test_client):
    test_client.mock_response(status_code=204)
    test_client.synchronise_device_state()

    headers = dict(list(test_client.connection.recent_stream.headers.items()))

    assert headers == {
        b':method': b'GET',
        b':scheme': b'https',
        b':authority': b'avs-alexa-eu.amazon.com',
        b':path': b'/v20160207/events',
        b'content-type': b'multipart/form-data; boundary=boundary',
        b'custom_header_one': b'value',
    }
    parsed = parse_multipart(
        body=test_client.connection._sock.queue[1],
        content_type=headers[b'content-type'].decode(),
    )

    assert parsed.parts[0].headers == {
        b'Content-Disposition': (
            b'form-data; name="metadata"; filename="metadata"'
        ),
        b'Content-Type': b'application/json'
    }

    assert json.loads(parsed.parts[0].content.decode()) == {
        'event': {
            'header': {
                'messageId': '',
                'name': 'SynchronizeState',
                'namespace': 'System'
            },
            'payload': {}
        },
        'context': [
            {
                'header': {
                    'name': 'PlaybackState',
                    'namespace': 'AudioPlayer'
                },
                'payload': {
                    'token': '',
                    'offsetInMilliseconds': 0,
                    'playerActivity': 'IDLE'
                }
            },
            {
                'header': {
                    'name': 'VolumeState',
                    'namespace': 'Speaker'
                },
                'payload': {
                    'muted': False,
                    'volume': 100
                }
            },
            {
                'header': {
                    'name': 'SpeechState',
                    'namespace': 'SpeechSynthesizer'
                },
                'payload': {
                    'token': '',
                    'offsetInMilliseconds': 0,
                    'playerActivity': 'FINISHED'
                }
            }
        ]
    }


def test_send_audio_file(test_client, audio_file):
    test_client.mock_response(status_code=200)

    with patch.object(test_client, 'parse_response'):  # test request only
        test_client.send_audio_file(audio_file)

    headers = dict(list(test_client.connection.recent_stream.headers.items()))

    assert headers == {
        b':method': b'POST',
        b':scheme': b'https',
        b':authority': b'avs-alexa-eu.amazon.com',
        b':path': b'/v20160207/events',
        b'content-type': b'multipart/form-data; boundary=boundary',
        b'custom_header_one': b'value',
    }
    parsed = parse_multipart(
        body=test_client.connection._sock.queue[1],
        content_type=headers[b'content-type'].decode(),
    )

    assert parsed.parts[0].headers == {
        b'Content-Type': b'application/json;',
        b'Content-Disposition': (
            b'form-data; name="request"; filename="request"'
        )
    }

    assert json.loads(parsed.parts[0].content.decode()) == {
        'event': {
            'payload': {
                'profile': 'CLOSE_TALK',
                'format': 'AUDIO_L16_RATE_16000_CHANNELS_1'
            },
            'header': {
                'namespace': 'SpeechRecognizer',
                'dialogRequestId': 'dialogue-id',
                'name': 'Recognize',
                'messageId': 'message-id'
            }
        },
        'context': [
            {
                'payload': {
                    'offsetInMilliseconds': 0,
                    'token': '',
                    'playerActivity': 'IDLE'
                },
                'header': {
                    'namespace': 'AudioPlayer',
                    'name': 'PlaybackState'
                }
            },
            {
                'payload': {
                    'volume': 100,
                    'muted': False
                },
                'header': {
                    'namespace': 'Speaker',
                    'name': 'VolumeState'
                }
            },
            {
                'payload': {
                    'offsetInMilliseconds': 0,
                    'token': '',
                    'playerActivity': 'FINISHED'
                },
                'header': {
                    'namespace': 'SpeechSynthesizer',
                    'name': 'SpeechState'
                }
            }
        ]
    }

    assert parsed.parts[1].headers == {
        b'Content-Type': b'application/octet-stream',
        b'Content-Disposition': b'form-data; name="audio"; filename="audio"'
    }
    assert parsed.parts[1].content == b'things'


def test_send_audio_204_response(test_client, audio_file):
    test_client.mock_response(status_code=204)
    response = test_client.send_audio_file(audio_file)

    assert response is None


@pytest.mark.parametrize(
    "status",  [code for code in range(200, 600) if code not in [200, 204]]
)
def test_send_audio_non_200_response(status, audio_file, test_client):
    test_client.mock_response(status_code=status)

    with pytest.raises(HTTPError):
        test_client.send_audio_file(audio_file)


@pytest.mark.skip()
def test_parse_response_200():
    # todo: get valid alexa response and mock the response
    pass


@freeze_time(datetime(3012, 1, 14, 12, 0, 0))
def test_send_audio_file_updates_ping_deadline(test_client, audio_file):
    assert test_client.ping_deadline is None

    test_client.mock_response(status_code=204)
    with patch.object(test_client, 'parse_response'):  # test request only
        test_client.send_audio_file(audio_file)

        assert test_client.ping_deadline.isoformat() == '3012-01-14T12:04:00'


@freeze_time(datetime(2012, 1, 14, 12, 0, 1))
@pytest.mark.parametrize('ping_deadline, expected', [
    [None, False],
    [datetime(2012, 1, 14, 12, 0, 2), False],
    [datetime(2012, 1, 14, 12, 0, 1), True],
    [datetime(2012, 1, 14, 12, 0, 0), True],
])
def test_should_ping(test_client, ping_deadline, expected):
    test_client.ping_deadline = ping_deadline

    assert test_client.should_ping() == expected


def test_ping(test_client):
    # TODO: confirm ping responds with 200
    test_client.mock_response(status_code=200)

    test_client.ping()

    # first part is the frame header (generated in frame serialization)
    assert test_client.connection._sock.queue[0] == (
        b'\x00\x00\x08\x06\x00\x00\x00\x00\x00********'
    )


def test_get_headers(client):
    with patch.object(client.authenticator, 'get_authentication_headers') as m:
        client.get_headers()

        assert m.call_count == 1


def test_generate_dialogue_id(client):
    # test it does not raise exception
    client.generate_dialogue_id()


def test_generate_message_id(client):
    # test it does not raise exception
    client.generate_message_id()
