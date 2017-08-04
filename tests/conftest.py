import requests_mock
import pytest


@pytest.fixture
def requests_mocker():
    m = requests_mock.mock()
    m.start()
    yield m
    m.stop()
