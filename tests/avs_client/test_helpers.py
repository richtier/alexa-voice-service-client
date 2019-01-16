from copy import deepcopy
import json
from unittest import mock

import pytest
from requests_toolbelt import MultipartEncoder

from avs_client.avs_client import helpers
from tests.avs_client import fixtures


@pytest.fixture
def audio_attachment():
    return mock.Mock()


def test_directive():
    directive = helpers.Directive(
        content=fixtures.speak_one_directive['directive']
    )

    assert directive.name == 'Speak'


def test_speak_directive(audio_attachment):
    directive = helpers.SpeakDirective(
        content=fixtures.speak_one_directive['directive'],
        audio_attachment=audio_attachment,
    )

    assert directive.audio_attachment == audio_attachment
    assert directive.name == 'Speak'


def test_play_directive(audio_attachment):
    directive = helpers.PlayDirective(
        content=fixtures.play_one_directive['directive'],
        audio_attachment=audio_attachment,
    )

    assert directive.audio_attachment == audio_attachment
    assert directive.name == 'Play'


def test_expect_speech_directive():
    directive = helpers.ExpectSpeechDirective(
        content=fixtures.expect_speech_directive['directive']
    )

    assert directive.dialog_request_id == '43c47763-8f55-4adc-84fb-2c34a615f93'
    assert directive.name == 'ExpectSpeech'


def test_avs_multipart_decoder():
    unhandled_directive = deepcopy(fixtures.speak_one_directive)
    unhandled_directive['directive']['header']['name'] = 'SomethingElse'

    multipart_response = MultipartEncoder(
        fields=[
            (
                'diretive-one', (
                    'directive-one',
                    json.dumps(fixtures.speak_one_directive),
                    'application/json',
                ),
            ),
            (
                'directive-two', (
                    'directive-two',
                    json.dumps(fixtures.play_one_directive),
                    'application/json',
                ),
            ),
            (
                'directive-three', (
                    'directive-three',
                    json.dumps(fixtures.expect_speech_directive),
                    'application/json',
                ),
            ),
            (
                'directive-four', (
                    'directive-four',
                    json.dumps(unhandled_directive),
                    'application/json',
                ),
            ),
            (
                'directive-five', (
                    'directive-five',
                    fixtures.audio_response_data,
                    'application/octet-stream',
                    {'Content-ID': '<DailyBriefingPrompt.ChannelIntroduction.5c4c5f3e-0c0f-4dac-b0e0-ba70065b8bc0:Say:DAILYBRIEFING:DailyBriefingIntroduction_1708175498>'},  # noqa
                )
            ),
            (
                'directive-six', (
                    'directive-six',
                    fixtures.audio_response_data,
                    'application/octet-stream',
                    {'Content-ID': '<DeviceTTSRenderer_bf8529e6-0708-4ac3-93a0-e57b0aff5ef4_1934409815>'},  # noqa
                )
            )
        ],
    )

    response = mock.Mock(
        headers={
            'access-control-allow-origin': '*',
            'x-amzn-requestid': '06aaf3fffec6be28-00003161-00006c28',
            'content-type': [bytes(multipart_response.content_type, 'utf8')],
        },
        **{'read.return_value': multipart_response.to_string()},
    )

    directives = helpers.AVSMultipartDecoder(response=response).directives

    directive = next(directives)
    assert directive.name == 'Speak'
    assert isinstance(directive, helpers.SpeakDirective)

    directive = next(directives)
    assert directive.name == 'Play'
    assert isinstance(directive, helpers.PlayDirective)

    directive = next(directives)
    assert directive.name == 'ExpectSpeech'
    assert isinstance(directive, helpers.ExpectSpeechDirective)

    directive = next(directives)
    assert directive.name == 'SomethingElse'
    assert isinstance(directive, helpers.Directive)
