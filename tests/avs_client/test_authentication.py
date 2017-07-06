from unittest.mock import patch

from freezegun import freeze_time
import pytest
from requests.exceptions import HTTPError

from avs_client.authentication import AlexaVoiceServiceTokenAuthenticator


@pytest.fixture
def token_retrieve_200(requests_mocker):
    return requests_mocker.post(
        AlexaVoiceServiceTokenAuthenticator.url, json={'access_token': 123}
    )


@pytest.fixture
def token_retrieve_400(requests_mocker):
    return requests_mocker.post(
        AlexaVoiceServiceTokenAuthenticator.url, status_code=400
    )


# AlexaVoiceServiceTokenAuthenticator
def test_url():
    authenticator = AlexaVoiceServiceTokenAuthenticator(
        client_id='debug', secret='debug', refresh_token='debug'
    )

    assert authenticator.url == "https://api.amazon.com/auth/o2/token"


# AlexaVoiceServiceTokenAuthenticator
def test_retrieve_api_token_posts_expected_data(token_retrieve_200):
    authenticator = AlexaVoiceServiceTokenAuthenticator(
        client_id='test_client_id',
        secret='test_secret',
        refresh_token='test_refresh_token',
    )

    authenticator.retrieve_api_token()

    assert token_retrieve_200.last_request.json() == {
        'client_id': 'test_client_id',
        'client_secret': 'test_secret',
        'refresh_token': 'test_refresh_token',
        'grant_type': 'refresh_token',
    }


# AlexaVoiceServiceTokenAuthenticator
def test_retrieve_api_token_returns_access_token(token_retrieve_200):
    authenticator = AlexaVoiceServiceTokenAuthenticator(
        client_id='test_client_id',
        secret='test_secret',
        refresh_token='test_refresh_token',
    )

    assert authenticator.retrieve_api_token() == 123


# AlexaVoiceServiceTokenAuthenticator
def test_retrieve_api_token_handles_bad_response(token_retrieve_400):
    authenticator = AlexaVoiceServiceTokenAuthenticator(
        client_id='test_client_id',
        secret='test_secret',
        refresh_token='test_refresh_token',
    )
    with pytest.raises(HTTPError):
        authenticator.retrieve_api_token()


# AlexaVoiceServiceTokenAuthenticator
@patch.object(AlexaVoiceServiceTokenAuthenticator, 'retrieve_api_token')
def test_prefetch_api_token(mock_retrieve_api_token):
    authenticator = AlexaVoiceServiceTokenAuthenticator(
        client_id='debug', secret='debug', refresh_token='debug'
    )

    authenticator.prefetch_api_token()

    assert mock_retrieve_api_token.call_count == 1


# AlexaVoiceServiceTokenAuthenticator
def test_get_authentication_headers(token_retrieve_200):
    authenticator = AlexaVoiceServiceTokenAuthenticator(
        client_id='debug', secret='debug', refresh_token='debug'
    )

    headers = authenticator.get_authentication_headers()

    assert headers == {'Authorization': 'Bearer 123'}


# AlexaVoiceServiceTokenAuthenticator
def test_retrieve_api_token_expiring_memo(token_retrieve_200):
    authenticator = AlexaVoiceServiceTokenAuthenticator(
        client_id='debug', secret='debug', refresh_token='debug'
    )

    with freeze_time('3012-01-14 12:00:00'):
        authenticator.retrieve_api_token()
        authenticator.retrieve_api_token()
    assert len(token_retrieve_200.request_history) == 1

    with freeze_time('3012-01-14 13:00:00'):
        authenticator.retrieve_api_token()
    assert len(token_retrieve_200.request_history) == 2

    with freeze_time('3012-01-14 13:30:00'):
        authenticator.retrieve_api_token()
    assert len(token_retrieve_200.request_history) == 2

    with freeze_time('3012-01-14 14:00:00'):
        authenticator.retrieve_api_token()
    assert len(token_retrieve_200.request_history) == 3
