class DeviceManager:
    def get_device_state(self):
        # https://developer.amazon.com/public/solutions/alexa/alexa-voice-service/reference/context
        return [
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
        ]
