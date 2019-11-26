from io import BytesIO
from unittest import mock

import pytest

from alexa_client.alexa_client.client import AlexaClient
from alexa_client.alexa_client import constants


@pytest.fixture
def client():
    class TestAlexaClient(AlexaClient):
        authentication_manager_class = mock.Mock()
        device_manager_class = mock.Mock()
        connection_manager_class = mock.Mock()
        ping_manager_class = mock.Mock()

    client = TestAlexaClient(
        client_id='test_client_id',
        secret='test_secret',
        refresh_token='test_refresh_token',
    )

    client.ping_manager.update_ping_deadline = mock.MagicMock()
    return client


def test_client_authentication_manager(client):
    assert client.authentication_manager_class.call_count == 1
    assert client.authentication_manager_class.call_args == mock.call(
        client_id='test_client_id',
        secret='test_secret',
        refresh_token='test_refresh_token',
    )


def test_base_url(client):

    class TestAlexaClient(AlexaClient):
        authentication_manager_class = mock.Mock()
        device_manager_class = mock.Mock()
        connection_manager_class = mock.Mock()
        ping_manager_class = mock.Mock()

    client = TestAlexaClient(
        client_id='test_client_id',
        secret='test_secret',
        refresh_token='test_refresh_token',
        base_url=constants.BASE_URL_NORTH_AMERICA
    )
    client.ping_manager.update_ping_deadline = mock.MagicMock()

    client.connect()

    assert client.connection_manager.create_connection.call_count == 1
    assert client.connection_manager.create_connection.call_args == mock.call(
        base_url=constants.BASE_URL_NORTH_AMERICA
    )


def test_client_connect(client):
    client.connect()

    assert client.authentication_manager.prefetch_api_token.call_count == 1
    assert (
        client.connection_manager.establish_downchannel_stream.call_count == 1
    )
    assert client.connection_manager.create_connection.call_args == mock.call(
        base_url=None
    )
    assert client.connection_manager.synchronise_device_state.call_count == 1


def test_client_establish_downchannel_stream(client):
    client.authentication_manager.get_headers.return_value = {'auth': 'value'}

    client.establish_downchannel_stream()
    connection_manager = client.connection_manager

    assert connection_manager.establish_downchannel_stream.call_args == (
        mock.call(authentication_headers={'auth': 'value'})
    )


def test_client_synchronise_device_state(client):
    client.authentication_manager.get_headers.return_value = {'auth': 'value'}
    client.device_manager.get_device_state.return_value = {'device': 'state'}

    client.synchronise_device_state()
    connection_manager = client.connection_manager

    assert connection_manager.synchronise_device_state.call_args == mock.call(
        device_state={'device': 'state'},
        authentication_headers={'auth': 'value'},
    )
    assert client.ping_manager.update_ping_deadline.call_count == 1


def test_client_send_audio_file(client):
    client.authentication_manager.get_headers.return_value = {'auth': 'value'}
    client.device_manager.get_device_state.return_value = {'device': 'state'}

    audio_file = BytesIO(b'things')
    client.send_audio_file(
        audio_file,
        dialog_request_id='dialog-id'
    )

    assert client.connection_manager.send_audio_file.call_args == mock.call(
        audio_file=audio_file,
        device_state={'device': 'state'},
        authentication_headers={'auth': 'value'},
        dialog_request_id='dialog-id',
        distance_profile=constants.CLOSE_TALK,
        audio_format=constants.PCM,
    )
    assert client.ping_manager.update_ping_deadline.call_count == 1


def test_client_send_audio_file_non_defaults(client):
    client.authentication_manager.get_headers.return_value = {'auth': 'value'}
    client.device_manager.get_device_state.return_value = {'device': 'state'}

    audio_file = BytesIO(b'things')
    client.send_audio_file(
        audio_file,
        dialog_request_id='dialog-id',
        distance_profile=constants.FAR_FIELD,
        audio_format=constants.OPUS,
    )

    assert client.connection_manager.send_audio_file.call_args == mock.call(
        audio_file=audio_file,
        device_state={'device': 'state'},
        authentication_headers={'auth': 'value'},
        dialog_request_id='dialog-id',
        distance_profile=constants.FAR_FIELD,
        audio_format=constants.OPUS,
    )
    assert client.ping_manager.update_ping_deadline.call_count == 1


@mock.patch('alexa_client.alexa_client.client.warnings.warn')
def test_conditional_ping(mock_warn, client):

    client.conditional_ping()

    assert mock_warn.call_count == 1
    assert mock_warn.call_args == mock.call(
        'Deprecated. Removing in v2.0.0.', DeprecationWarning
    )


def test_ping(client):
    client.authentication_manager.get_headers.return_value = {'auth': 'value'}

    client.ping()

    assert client.connection_manager.ping.call_count == 1
    assert client.connection_manager.ping.call_args == mock.call(
        authentication_headers={'auth': 'value'}
    )
