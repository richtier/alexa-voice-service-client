import json

from requests_toolbelt import MultipartEncoder


audio_response_data = open('tests/resources/test.mp3', 'rb').read()

speak_one_directive = {
    'directive': {
        'header': {
            'namespace': 'SpeechSynthesizer',
            'name': 'Speak',
            'messageId': '3009890b-a556-48bd-87f6-cae9476f3cd8',  # noqa
            'dialogRequestId': 'f3bd01b3-fb8b-4468-ba30-32bad766b3e6'  # noqa
        },
        'payload': {
            'url': 'cid:DeviceTTSRenderer_bf8529e6-0708-4ac3-93a0-e57b0aff5ef4_1934409815',  # noqa
            'format': 'AUDIO_MPEG',
            'token': 'amzn1.as-ct.v1.Domain:Application:Notifications#ACRI#DeviceTTSRenderer_bf8529e6-0708-4ac3-93a0-e57b0aff5ef4'  # noqa
        }
    }
}

play_one_directive = {
    'directive': {
        'header': {
            'namespace': 'AudioPlayer',
            'name': 'Play',
            'messageId': 'd07467ff-fe23-40c4-98b3-b1966f4341bb',  # noqa
            'dialogRequestId': '43c47763-8f55-4adc-84fb-2c34a615f932'  # noqa
        },
        'payload': {
            'audioItem': {
                'audioItemId': 'amzn1.as-ct.v1.Domain:Application:DailyBriefing:TTS#ACRI#url#ACRI#DailyBriefingPrompt.5c4c5f3e-0c0f-4dac-b0e0-ba70065b8bc0:ChannelItem:0:0',  # noqa
                'stream': {
                    'offsetInMilliseconds': 0,
                    'expiryTime': '2018-12-31T17:20:14+0000',
                    'url': 'https://www.example.com/some/mp3.mp3',  # noqa
                    'token': 'amzn1.as-ct.v1.Domain:Application:DailyBriefing:TTS#ACRI#url#ACRI#DailyBriefingPrompt.5c4c5f3e-0c0f-4dac-b0e0-ba70065b8bc0:ChannelIntroduction:0',  # noqa
                    'caption': None
                }
            },
            'playBehavior': 'REPLACE_ALL'
        }
    }
}

play_two_directive = {
    'directive': {
        'header': {
            'namespace': 'AudioPlayer',
            'name': 'Play',
            'messageId': '511b6df2-f187-43be-89b6-53b20df90dd3',  # noqa
            'dialogRequestId': '43c47763-8f55-4adc-84fb-2c34a615f932'  # noqa
        },
        'payload': {
            'playBehavior': 'ENQUEUE',
            'audioItem': {
                'audioItemId': 'amzn1.as-ct.v1.Domain:Application:DailyBriefing:TTS#ACRI#url#ACRI#DailyBriefingPrompt.5c4c5f3e-0c0f-4dac-b0e0-ba70065b8bc0:ChannelItem:0:0',  # noqa
                'stream': {
                    'offsetInMilliseconds': 0,
                    'expiryTime': '2018-12-31T17:20:14+0000',
                    'url': 'https://www.example.com/some/other/mp3.mp3',  # noqa
                    'token': 'amzn1.as-ct.v1.Domain:Application:DailyBriefing:TTS#ACRI#url#ACRI#DailyBriefingPrompt.5c4c5f3e-0c0f-4dac-b0e0-ba70065b8bc0:ChannelItem:0:0',  # noqa
                    'caption': None
                }
            }
        }
    }
}

speak_two_directive = {
    'directive': {
        'header': {
            'namespace': 'SpeechSynthesizer',
            'name': 'Speak',
            'messageId': '1c1cf4d9-4c8a-4123-8fd6-e9c46597ca59',
            'dialogRequestId': '43c47763-8f55-4adc-84fb-2c34a615f932'
        },
        'payload': {
            'url': 'cid:DailyBriefingPrompt.ChannelIntroduction.5c4c5f3e-0c0f-4dac-b0e0-ba70065b8bc0:Say:DAILYBRIEFING:DailyBriefingIntroduction_1708175498',  # noqa
            'format': 'AUDIO_MPEG',
            'token': 'amzn1.as-ct.v1.Domain:Application:DailyBriefing:TTS#ACRI#DailyBriefingPrompt.ChannelIntroduction.5c4c5f3e-0c0f-4dac-b0e0-ba70065b8bc0:Say:DAILYBRIEFING:DailyBriefingIntroduction'  # noqa
        }
    }
}

expect_speech_directive = {
    'directive': {
        'header': {
            'namespace': 'SpeechRecognizer',
            'name': 'ExpectSpeech',
            'messageId': '1c1cf4d9-4c8a-4123-8fd6-e9c46597ca57',
            'dialogRequestId': '43c47763-8f55-4adc-84fb-2c34a615f93'
        },
        'payload': {
            'timeoutInMilliseconds': 123,
            'initiator': {
                'type': 'something',
                'payload': {
                    'token': 'some-token',
                }
            }
        }
    }
}

flash_briefing_multipart = MultipartEncoder(
    fields=[
        (
            'diretive-one', (
                'directive-one',
                json.dumps(speak_two_directive),
                'application/json',
            ),
        ),
        (
            'directive-two', (
                'directive-two',
                json.dumps(play_one_directive),
                'application/json',
            ),
        ),
        (
            'directive-three', (
                'directive-three',
                json.dumps(play_two_directive),
                'application/json',
            ),
        ),
        (
            'directive-four', (
                'directive-four',
                audio_response_data,
                'application/octet-stream',
                {'Content-ID': '<DailyBriefingPrompt.ChannelIntroduction.5c4c5f3e-0c0f-4dac-b0e0-ba70065b8bc0:Say:DAILYBRIEFING:DailyBriefingIntroduction_1708175498>'},  # noqa
            )
        )
    ],
)

time_multipart = MultipartEncoder(
    fields=[
        (
            'directive-one', (
                'directive-one',
                json.dumps(speak_one_directive),
                'application/json'
            )
        ),
        (
            'directive-two', (
                'directive-two',
                audio_response_data,
                'application/octet-stream',
                {'Content-ID': '<DeviceTTSRenderer_bf8529e6-0708-4ac3-93a0-e57b0aff5ef4_1934409815>'},  # noqa
            )
        )
    ]
)
