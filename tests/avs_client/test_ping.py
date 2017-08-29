from datetime import datetime

from freezegun import freeze_time
import pytest

from avs_client.avs_client import ping


@pytest.fixture
def manager():
    return ping.PingManager()


@freeze_time(datetime(2012, 1, 14, 12, 0, 1))
@pytest.mark.parametrize('ping_deadline,expected', [
    [None, False],
    [datetime(2012, 1, 14, 12, 0, 2), False],
    [datetime(2012, 1, 14, 12, 0, 1), True],
    [datetime(2012, 1, 14, 12, 0, 0), True],
])
def test_should_ping(manager, ping_deadline, expected):
    manager.ping_deadline = ping_deadline

    assert manager.should_ping() == expected


@freeze_time(datetime(2012, 1, 14, 12, 0, 1))
def test_update_ping_deadline(manager):
    assert manager.ping_deadline is None

    with manager.update_ping_deadline():
        pass

    assert manager.ping_deadline == datetime(2012, 1, 14, 12, 4, 1)
