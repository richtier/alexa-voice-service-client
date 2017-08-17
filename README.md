# alexa-voice-service-client #
Python Client for Alexa Voice Service (AVS)

## Installation ##
```sh
pip install git+https://github.com/richtier/alexa-browser-client.git@0.2.0#egg=alexa_browser_client
```

## Usage ##

```py
from avs_client import AlexaVoiceServiceClient


alexa_client = AlexaVoiceServiceClient(
    client_id='my-client-id',
    secret='my-secret',
    refresh_token='my-refresh-token',
)
alexa_client.connect()  # authenticate and other handshaking steps
with open('./tests/resource/alexa_what_time_is_it.wav', 'rb') as f:
    alexa_response_audio = alexa_client.send_audio_file(f)
with open('./output.wav', 'wb') as f:
    f.write(alexa_response_audio)
```

Now have a listen to `output.wave` and Alexa should tell you the time.

### Persistent AVS connection ##

Calling `alexa_client.connect()` creates a persistent HTTP2 connection to AVS. The connection will be closed by AVS if no frames are sent through it within five minutes. To keep the connection open call `alexa_client.alexa_client.conditional_ping()` to ping when the connection has not been used within the deadline:

```py
alexa_client.conditional_ping()
```

The ping code could be placed in a thread to ensure the connection stays open during long running processes:

```py
import threading


def ping_avs():
    while True:
        alexa_client.conditional_ping()

ping_thread = threading.Thread(target=ping_avs)
ping_thread.start()
```

For more information see AVS's documentation: https://developer.amazon.com/public/solutions/alexa/alexa-voice-service/docs/managing-an-http-2-connection

### Steaming audio to AVS ###
`alexa_client.send_audio_file` streaming uploads a file-like object to AVS for great latency. The file-like object can be an actual file on your filesystem, an in-memory BytesIo buffer containing audio from your microphone, or even audio streaming from [your browser over a websocket in real-time](https://github.com/richtier/alexa-browser-client).

AVS requires the audio data to be 16bit Linear PCM (LPCM16), 16kHz sample rate, single-channel, and little endian.

## Authentication ##

Instantiating the client requires some valid AVS authentication details:

| client kwarg | Notes                                                                |
| --------------- | ---------------------------------------------------------------------- |
| client_id     | See [AVS documentation](https://developer.amazon.com/public/solutions/alexa/alexa-voice-service/docs/authorizing-your-alexa-enabled-product-from-a-website#lwa)                               |
| secret        | See [AVS documentation](https://developer.amazon.com/public/solutions/alexa/alexa-voice-service/docs/authorizing-your-alexa-enabled-product-from-a-website#lwa)                                |
| refresh_token | Set this to the value returned when you [retrieve your refresh token](#refresh-token) |

### Refresh token ##

When the client authenticates with AVS using a `client_id` and `client_secret` AVS returns an access token that authorizes subsequent requests. The access token expires after an hour. To automatically generate a new access token once the old one expires, a  `refresh_token` can be exposed. To enable this functionality specify `refresh_token` when instantiating the client.

To get your refresh token for the first time you will need to authenticate with Amazon via their web interface. To do this run 

```sh
python ./avs_client/refreshtoken/serve.py \
    --device-type-id=enter-device-type-id-here \
    --client-id=enter-client-id-here \
    --client-secret=enter-client-secret-here
```

Then go to `http://localhost:8000` and follow the on-screen instructions. Use the `refresh_token` returned by Amazon when you instantiate the client.

## Other projects ##

This library is used by [alexa-browser-client](https://github.com/richtier/alexa-browser-client), which allows you to talk to Alexa from your browser.
