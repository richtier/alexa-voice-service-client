# Alexa Voice Service Client

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]

**Python Client for Alexa Voice Service (AVS)**

---

## Installation
```sh
pip install alexa_client
```

or if you want to run the demos:

```sh
pip install alexa_client[demo]
```

## Usage

### File audio ###
```py
from alexa_client import AlexaClient

client = AlexaClient(
    client_id='my-client-id',
    secret='my-secret',
    refresh_token='my-refresh-token',
)
client.connect()  # authenticate and other handshaking steps
with open('./tests/resources/alexa_what_time_is_it.wav', 'rb') as f:
    for i, directive in enumerate(client.send_audio_file(f)):
        if directive.name in ['Speak', 'Play']:
            with open(f'./output_{i}.mp3', 'wb') as f:
                f.write(directive.audio_attachment)
```

Now listen to `output_0.wav` and Alexa should tell you the time.

### Microphone audio

```py
import io

from alexa_client import AlexaClient
import pyaudio


def callback(in_data, frame_count, time_info, status):
    buffer.write(in_data)
    return (in_data, pyaudio.paContinue)

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    stream_callback=callback,
)

client = AlexaClient(
    client_id='my-client-id',
    secret='my-secret',
    refresh_token='my-refresh-token',
)

buffer = io.BytesIO()
try:
    stream.start_stream()
    print('listening. Press CTRL + C to exit.')
    client.connect()
    for i, directive in enumerate(client.send_audio_file(buffer)):
        if directive.name in ['Speak', 'Play']:
            with open(f'./output_{i}.mp3', 'wb') as f:
                f.write(directive.audio_attachment)
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
```

### Multi-step requests

An Alexa command may relate to a previous command e.g,

[you] "Alexa, play twenty questions"
[Alexa] "Is it a animal, mineral, or vegetable?"
[you] "Mineral"
[Alexa] "Is it valuable"
[you] "No"
[Alexa] "is it..."

This can be achieved by passing the same dialog request ID to multiple `send_audio_file` calls:

```py
from alexa_client.alexa_client import helpers

dialog_request_id = helpers.generate_unique_id()
directives_one = client.send_audio_file(audio_one, dialog_request_id=dialog_request_id)
directives_two = client.send_audio_file(audio_two, dialog_request_id=dialog_request_id)
directives_three = client.send_audio_file(audio_three, dialog_request_id=dialog_request_id)

```

Run the streaming microphone audio demo to use this feature:

```sh
pip install alexa_client[demo]
python -m alexa_client.demo.streaming_microphone \
    --client-id="{enter-client-id-here}" \
    --client-secret="{enter-client-secret-here}" \
    --refresh-token="{enter-refresh-token-here}"
```

### ASR Profiles
Automatic Speech Recognition (ASR) profiles optimized for user speech from varying distances. By default CLOSE_TALK is used but this can be specified:

```
from alexa_client import constants

client.send_audio_file(
    audio_file=audio_file,
    distance_profile=constants.NEAR_FIELD,  # or constants.FAR_FIELD
)
```

### Audio format

By default PCM audio format is assumed, but OPUS can be specified:

```
from alexa_client import constants

client.send_audio_file(
    audio_file=audio_file,
    audio_format=constants.OPUS,
)
```

When PCM format is specified the audio should be 16bit Linear PCM (LPCM16), 16kHz sample rate, single-channel, and little endian.

When OPUS forat is specified the audio should be 16bit Opus, 16kHz sample rate, 32k bit rate, and little endian.

### Base URL

`base_url` can be set to improve latency. Choose a region closest to your location.

```
from alexa_client.alexa_client import constants

client = AlexaClient(
    client_id='my-client-id',
    secret='my-secret',
    refresh_token='my-refresh-token',
    base_url=constants.BASE_URL_ASIA
)
```

The default base URL is Europe. The available constants are BASE_URL_EUROPE, BASE_URL_ASIA and BASE_URL_NORTH_AMERICA but you can pass any string if required.

[Read more](https://developer.amazon.com/docs/alexa-voice-service/api-overview.html#endpoints)

## Authentication

To use AVS you must first have a [developer account](http://developer.amazon.com). Then register your product [here](https://developer.amazon.com/avs/home.html#/avs/products/new). Choose "Application" under "Is your product an app or a device"?

The client requires your `client_id`, `secret` and `refresh_token`:

| client kwarg    | Notes |
| --------------- | ------------------------------------- |
| `client_id`     | Retrieve by clicking on the your product listed [here](https://developer.amazon.com/avs/home.html#/avs/home) |
| `secret`        | Retrieve by clicking on the your product listed [here](https://developer.amazon.com/avs/home.html#/avs/home) |
| `refresh_token` | You must generate this. [See below](#refresh-token) |

### Refresh token ###

You will need to login to Amazon via a web browser to get your refresh token.

To enable this first go [here](https://developer.amazon.com/avs/home.html#/avs/home) and click on your product to set some security settings under `Security Profile`:

| setting             | value                           |
| ------------------- | --------------------------------|
| Allowed Origins     | http://localhost:9000           |
| Allowed Return URLs | http://localhost:9000/callback/ |

Note what you entered for Product ID under Product Information, as this will be used as the device-type-id (case sensitive!)

Then run:

```sh
python -m alexa_client.refreshtoken.serve \
    --device-type-id="{enter-device-type-id-here}" \
    --client-id="{enter-client-id-here}" \
    --client-secret="{enter-client-secret-here}"
```

Follow the on-screen instructions shown at `http://localhost:9000` in your web browser. 
On completion Amazon will return your `refresh_token` - which you will require to [send audio](#file-audio) or [recorded voice](#microphone-audio).

## Steaming audio to AVS
`AlexaClient.send_audio_file` streaming uploads a file-like object to AVS for great latency. The file-like object can be an actual file on your filesystem, an in-memory BytesIo buffer containing audio from your microphone, or even audio streaming from [your browser over a websocket in real-time](https://github.com/richtier/alexa-browser-client).

## Persistent AVS connection

Calling `AlexaClient.connect` creates a persistent connection to AVS. A thread runs that pings AVS after 4 minutes of no request being made to AVS. This prevents the connection getting forcefully closed due to inactivity.

## Unit test ##

To run the unit tests, call the following commands:

```sh
git clone git@github.com:richtier/alexa-voice-service-client.git
make test_requirements
pytest
```

## Other projects ##

This library is used by [alexa-browser-client](https://github.com/richtier/alexa-browser-client), which allows you to talk to Alexa from your browser.

[code-climate-image]: https://codeclimate.com/github/richtier/alexa-voice-service-client/badges/gpa.svg
[code-climate]: https://codeclimate.com/github/richtier/alexa-voice-service-client

[circle-ci-image]: https://circleci.com/gh/richtier/alexa-voice-service-client/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/richtier/alexa-voice-service-client/tree/master

[codecov-image]: https://codecov.io/gh/richtier/alexa-voice-service-client/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/richtier/alexa-voice-service-client

