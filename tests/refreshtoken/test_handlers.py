import re
import threading
import urllib

import pytest
import requests

from alexa_client.refreshtoken import handlers, helpers, http_server


@pytest.fixture(scope='session')
def server():
    return http_server.AmazonLoginHttpServer(
        server_address=('localhost', 9000),
        RequestHandlerClass=handlers.AmazonAlexaServiceLoginHandler,
        client_id='client-id-here',
        client_secret='client-secret-here',
        device_type_id='device-type-id-here',
        callback_url='http://localhost:9000/callback/',
    )


@pytest.fixture(scope='session')
def background_server(server):
    def thread_function():
        server.serve_forever()

    thread = threading.Thread(target=thread_function)
    thread.start()
    try:
        yield
    finally:
        thread._is_stopped = True


@pytest.fixture
def amazon_request_200(requests_mocker):
    return requests_mocker.post(
        url=helpers.AmazonOauth2RequestManager.authorization_grant_url,
        status_code=200,
        json={
            'refresh_token': 'my-refresh-token'
        }
    )


@pytest.fixture
def amazon_request_401(requests_mocker):
    return requests_mocker.post(
        url=helpers.AmazonOauth2RequestManager.authorization_grant_url,
        status_code=401,
        text='oops!'
    )


@pytest.fixture(autouse=True)
def allow_local_server_request(requests_mocker):
    requests_mocker.register_uri(
        'GET', re.compile('http://localhost:9000/'), real_http=True
    )


def test_routes_to_login(background_server):
    response = requests.get('http://localhost:9000/', allow_redirects=False)
    url = urllib.parse.unquote_plus(response.headers['Location'])
    assert url == (
        'https://www.amazon.com/ap/oa?client_id=client-id-here&'
        'scope=alexa:all&''scope_data={"alexa:all": {"productID": '
        '"device-type-id-here", "productInstanceAttributes": '
        '{"deviceSerialNumber": "001"}}}&response_type=code&'
        'redirect_uri=http://localhost:9000/callback/'
    )


def test_routes_to_404(background_server):
    response = requests.get('http://localhost:9000/a', allow_redirects=False)
    assert response.status_code == 404


def test_handle_callback_amazon_request(
    background_server, amazon_request_200, requests_mocker
):
    requests.get('http://localhost:9000/callback/?code=my-code')

    amazon_request = requests_mocker.request_history[1]
    assert amazon_request.json() == {
        'client_id': 'client-id-here',
        'client_secret': 'client-secret-here',
        'code': 'my-code',
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:9000/callback/',
    }


def test_handle_callback_200_response(background_server, amazon_request_200):
    response = requests.get('http://localhost:9000/callback/?code=my-code')

    assert response.status_code == 200
    assert response.content == b'refresh_token: my-refresh-token'


def test_handle_callback_non_200(background_server, amazon_request_401):
    response = requests.get('http://localhost:9000/callback/?code=my-code')
    assert response.status_code == 401
    assert response.content == b'oops!'
