# alexa-voice-service-client
Python Client for Alexa Voice Service (AVS)

## Installation
```
pip install git+https://github.com/richtier/alexa-browser-client.git@v0.1.0#egg=alexa_browser_client
```

## Usage

```
    alexa_client = AlexaVoiceServiceClient(
        client_id='my-client-id',
        secret='my-secret',
        refresh_token='my-refresh-token',
    )
    alexa_client.connect()  # authenticate, create downchannel stream, and other handshaking
    with open('/path/to/little_endian_16000_sample_rate_file.wav', 'rb') as f:
        alexa_response_audio = alexa_client.send_audio_file(f)
    with open('/path/to/output.wav', 'wb') as f:
        f.write(alexa_response_audio)
```

### Persistent AVS connection

Calling `alexa_client.connect()` creates a persistent HTTP2 connection to AVS. The connection will be closed by AVS if no frames are sent through it within five minutes. To keep the connection open call `alexa_client.ping()`. To avoid unnecessary pings `alexa_client.should_ping()` can be checked:

```
if alexa_client.should_ping():
    alexa_client.ping()
```

The ping code can be placed in a thread to ensure the connection stays open during long running processes:

```
import threading

def ping_avs(self):
    while True:
        if alexa_client.should_ping():
            alexa_client.ping()

ping_thread = threading.Thread(target=ping_avs)
ping_thread.start()
```

For more information see AVS's documentation: https://developer.amazon.com/public/solutions/alexa/alexa-voice-service/docs/managing-an-http-2-connection

### Steaming audio to AVS
`alexa_client.send_audio_file` streaming uploads a file-like object to AVS for great latency. The file-like object can be a file on your filesystem, an in-memory file streaming audio from your microphone in real-time, or even audio streaming from [your browser over a websocket in real-time](https://github.com/richtier/alexa-browser-client).

AVS requires the audio data to be 16bit Linear PCM (LPCM16), 16kHz sample rate, single-channel, and little endian.

## Authentication

Instantiating the client requires some valid AVS authentication details:

```
| client kwargs | Notes                                                                |
|---------------|----------------------------------------------------------------------|
| client_id     | See AVS documentation [link 1, below)                                |
| secret        | See AVS documentation [link 1, below)                                |
| refresh_token | Set this to the value returned when you retrieve your refresh token. |
```

[1] https://developer.amazon.com/public/solutions/alexa/alexa-voice-service/docs/authorizing-your-alexa-enabled-product-from-a-website#lwa


### Refresh token

When the client authenticates with AVS using a `client_id` and `client_secret` AVS returns an access token that authorizes subsequent requests. The access token expires after an hour. To automatically generate a new access token once the old one expires, a  `refresh_token` can be exposed. To enable this functionality set `ALEXA_VOICE_SERVICE_REFRESH_TOKEN`.

To get your refresh token for the first time you will need to authenticate with Amazon via their web interface. To do this run 

```
ALEXA_VOICE_SERVICE_DEVICE_TYPE_ID=enter-value-here ALEXA_VOICE_SERVICE_CLIENT_ID=enter-value-here ALEXA_VOICE_SERVICE_CLIENT_SECRET=enter-value-here python ./avs_client/refreshtoken/serve.py
```

Then go to `http://localhost:8000/amazon-login/` and follow the on-screen instructions. Set `ALEXA_VOICE_SERVICE_REFRESH_TOKEN` setting to the `refresh_token` value returned by Amazon.

## Other projects

This library is used by [alexa-browser-client](https://github.com/richtier/alexa-browser-client), which allows you to talk to Alexa from your browser.
