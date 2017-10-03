class DeviceManager:

    def build_device_state(self, context=None):
        # https://developer.amazon.com/public/solutions/alexa/alexa-voice-service/reference/context
        state = [
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
        if context:
            state.append(context)
        return state
