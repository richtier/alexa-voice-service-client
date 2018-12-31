from io import BytesIO
import json
from unittest.mock import patch

import pytest
from requests.exceptions import HTTPError

from avs_client.avs_client import connection
from tests.avs_client.helpers import parse_multipart, TestConnectionMixin
from tests.avs_client import fixtures


class TestConnectionManager(TestConnectionMixin, connection.ConnectionManager):
    @staticmethod
    def generate_dialogue_id():
        # override existing non-deterministic method
        return 'dialogue-id'

    @staticmethod
    def generate_message_id():
        # override existing non-deterministic method
        return 'message-id'


@pytest.fixture(autouse=True)
def some_mp3_stream_download(requests_mocker):
    return requests_mocker.get(
        'https://www.example.com/some/mp3.mp3',
        status_code=200,
        content=fixtures.audio_response_data,
    )


@pytest.fixture(autouse=True)
def some_other_mp3_stream_download(requests_mocker):
    return requests_mocker.get(
        'https://www.example.com/some/other/mp3.mp3',
        status_code=200,
        content=fixtures.audio_response_data,
    )


@pytest.fixture
def manager():
    return TestConnectionManager()


@pytest.fixture
def authentication_headers():
    return {'auth': 'value'}


@pytest.fixture
def device_state():
    return {'device': 'state'}


@pytest.fixture
def audio_file():
    return BytesIO(b'things')


def test_create_connection(manager):
    manager.create_connection()

    assert manager.connection.host == 'avs-alexa-eu.amazon.com'
    assert manager.connection.secure is True


def test_establish_downstream_conncetion(manager, authentication_headers):
    manager.create_connection()

    manager.establish_downchannel_stream(
        authentication_headers=authentication_headers
    )

    headers = dict(list(manager.connection.recent_stream.headers.items()))

    assert headers == {
        b':scheme': b'https',
        b':method': b'GET',
        b':path': b'/v20160207/directives',
        b':authority': b'avs-alexa-eu.amazon.com',
        b'auth': b'value',
    }


@pytest.mark.parametrize("status", [200, 204])
def test_synchronise_device_state(
    status, manager, authentication_headers, device_state
):
    manager.create_connection()
    manager.mock_response(status_code=status)

    manager.synchronise_device_state(
        authentication_headers=authentication_headers,
        device_state=device_state,
    )

    headers = dict(list(manager.connection.recent_stream.headers.items()))

    assert headers == {
        b':method': b'GET',
        b':scheme': b'https',
        b':authority': b'avs-alexa-eu.amazon.com',
        b':path': b'/v20160207/events',
        b'content-type': b'multipart/form-data; boundary=boundary',
        b'auth': b'value',
    }
    parsed = parse_multipart(
        body=manager.connection._sock.queue[1],
        content_type=headers[b'content-type'].decode(),
    )

    assert parsed.parts[0].headers == {
        b'Content-Disposition': (
            b'form-data; name="metadata"; filename="metadata"'
        ),
        b'Content-Type': b'application/json'
    }

    assert json.loads(parsed.parts[0].content.decode()) == {
        'context': device_state,
        'event': {
            'header': {
                'messageId': '',
                'name': 'SynchronizeState',
                'namespace': 'System'
            },
            'payload': {}
        },
    }


def test_send_audio_file(
    manager, audio_file, device_state, authentication_headers
):
    manager.create_connection()
    manager.mock_response(status_code=200)

    with patch.object(manager, 'parse_response'):  # test request only
        manager.send_audio_file(
            device_state=device_state,
            authentication_headers=authentication_headers,
            audio_file=audio_file,
        )

    headers = dict(list(manager.connection.recent_stream.headers.items()))

    assert headers == {
        b':method': b'POST',
        b':scheme': b'https',
        b':authority': b'avs-alexa-eu.amazon.com',
        b':path': b'/v20160207/events',
        b'content-type': b'multipart/form-data; boundary=boundary',
        b'auth': b'value',
    }
    parsed = parse_multipart(
        body=manager.connection._sock.queue[1],
        content_type=headers[b'content-type'].decode(),
    )

    assert parsed.parts[0].headers == {
        b'Content-Type': b'application/json;',
        b'Content-Disposition': (
            b'form-data; name="request"; filename="request"'
        )
    }

    assert json.loads(parsed.parts[0].content.decode()) == {
        'context': device_state,
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
    }

    assert parsed.parts[1].headers == {
        b'Content-Type': b'application/octet-stream',
        b'Content-Disposition': b'form-data; name="audio"; filename="audio"'
    }
    assert parsed.parts[1].content == b'things'


def test_speak_and_play_response_200(
    manager, audio_file, device_state, authentication_headers
):
    manager.create_connection()
    manager.mock_response(
        data=fixtures.flash_briefing_multipart.to_string(),
        headers=[
            (b'access-control-allow-origin', b'*'),
            (b'x-amzn-requestid', b'06aaf3fffec6be28-00003161-00006c28'),
            (b'content-type', fixtures.flash_briefing_multipart.content_type)
        ],
        status_code=200
    )

    directives = list(manager.send_audio_file(
        audio_file=audio_file,
        device_state=device_state,
        authentication_headers=authentication_headers,
    ))
    assert len(directives) == 3

    directive_one, directive_two, directive_three = directives

    assert directive_one.name == 'Speak'
    assert directive_one.get_content_id(directive_one.directive) == (
        '<DailyBriefingPrompt.ChannelIntroduction.'
        '5c4c5f3e-0c0f-4dac-b0e0-ba70065b8bc0:Say:DAILYBRIEFING:'
        'DailyBriefingIntroduction_1708175498>'
    )
    assert directive_one.audio_attachment == fixtures.audio_response_data

    assert directive_two.name == 'Play'
    assert directive_two.get_url(directive_two.directive) == (
        'https://www.example.com/some/mp3.mp3'
    )
    assert directive_two.audio_attachment == fixtures.audio_response_data

    assert directive_three.name == 'Play'
    assert directive_three.get_url(directive_three.directive) == (
        'https://www.example.com/some/other/mp3.mp3'
    )
    assert directive_three.audio_attachment == fixtures.audio_response_data


def test_parse_speak_response_200(
    manager, audio_file, device_state, authentication_headers
):
    manager.create_connection()

    manager.mock_response(
        data=fixtures.time_multipart.to_string(),
        headers=[
            (b'access-control-allow-origin', b'*'),
            (b'x-amzn-requestid', b'06aaf3fffec6be28-00003161-00006c28'),
            (b'content-type', fixtures.time_multipart.content_type)
        ],
        status_code=200
    )

    directives = manager.send_audio_file(
        audio_file=audio_file,
        device_state=device_state,
        authentication_headers=authentication_headers,
    )
    for directive in directives:
        assert directive.get_content_id(directive.directive) == (
            '<DeviceTTSRenderer_'
            'bf8529e6-0708-4ac3-93a0-e57b0aff5ef4_1934409815>'
        )
        assert directive.audio_attachment == fixtures.audio_response_data
        assert directive.name == 'Speak'


def test_send_audio_204_response(
    manager, audio_file, authentication_headers, device_state
):
    manager.create_connection()
    manager.mock_response(status_code=204)

    response = manager.send_audio_file(
        device_state=device_state,
        authentication_headers=authentication_headers,
        audio_file=audio_file,
    )

    assert response is None


@pytest.mark.parametrize(
    "status",  [code for code in range(200, 600) if code not in [200, 204]]
)
def test_send_audio_non_200_response(
    status, audio_file, manager, device_state, authentication_headers
):
    manager.create_connection()
    manager.mock_response(status_code=status)

    with pytest.raises(HTTPError):
        manager.send_audio_file(
            device_state=device_state,
            authentication_headers=authentication_headers,
            audio_file=audio_file,
        )


def test_ping(manager, authentication_headers):
    manager.create_connection()
    manager.mock_response(status_code=204)

    manager.ping(
        authentication_headers=authentication_headers
    )

    headers = dict(list(manager.connection.recent_stream.headers.items()))

    assert headers == {
        b':scheme': b'https',
        b':method': b'GET',
        b':path': b'/ping',
        b':authority': b'avs-alexa-eu.amazon.com',
        b'auth': b'value',
    }
