import pytest

from avs_client.avs_client import device


@pytest.fixture
def manager():
    return device.DeviceManager()


def test_default_device_state(manager):
    assert manager.build_device_state() == [
        {
            'header': {
                'namespace': 'AudioPlayer',
                'name': 'PlaybackState'
            },
            'payload': {
                'token': '',
                'offsetInMilliseconds': 0,
                'playerActivity': 'IDLE'
            }
        },
        {
            'header': {
                'namespace': 'Speaker',
                'name': 'VolumeState'
            },
            'payload': {
                'volume': 100,
                'muted': False,
            }
        },
        {
            'header': {
                'namespace': 'SpeechSynthesizer',
                'name': 'SpeechState'
            },
            'payload': {
                'token': '',
                'offsetInMilliseconds': 0,
                'playerActivity': 'FINISHED'
            }
        }
    ]


def test_default_device_state_extra_context(manager):
    context = {
        'header': {
            'namespace': 'Edgar',
            'name': 'RoomState'
        },
        'payload': {
            'room': 'kitchen'
        }
    }

    assert manager.build_device_state(context) == [
        {
            'header': {
                'namespace': 'AudioPlayer',
                'name': 'PlaybackState'
            },
            'payload': {
                'token': '',
                'offsetInMilliseconds': 0,
                'playerActivity': 'IDLE'
            }
        },
        {
            'header': {
                'namespace': 'Speaker',
                'name': 'VolumeState'
            },
            'payload': {
                'volume': 100,
                'muted': False,
            }
        },
        {
            'header': {
                'namespace': 'SpeechSynthesizer',
                'name': 'SpeechState'
            },
            'payload': {
                'token': '',
                'offsetInMilliseconds': 0,
                'playerActivity': 'FINISHED'
            }
        },
        {
            'header': {
                'namespace': 'Edgar',
                'name': 'RoomState'
            },
            'payload': {
                'room': 'kitchen'
            }
        }
    ]
