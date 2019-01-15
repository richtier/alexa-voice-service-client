from unittest import mock

import pytest

from avs_client.avs_client import ping
from resettabletimer import FakeTimer


class FakePingManager(ping.PingManagerMixin, FakeTimer):
    reset = mock.Mock()


@pytest.fixture
def ping_handler():
    return mock.Mock()


@pytest.fixture
def manager(ping_handler):
    return FakePingManager(100, ping_handler)


def test_update_ping_deadline(manager):
    manager.reset = mock.Mock()

    with manager.update_ping_deadline():
        pass

    assert manager.reset.call_count == 1


def test_call_resets_timer(manager, ping_handler):
    manager.start()

    manager.pass_time(100)

    assert ping_handler.call_count == 1
