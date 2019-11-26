# Changelog

## 1.5.0
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/35)
### Implemented enhancements
- Allow setting base_url when instantiating the client

## 1.4.1
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/34)
### Implemented enhancements
- Simplified makefile. Use direct `flake8` and `pytest` commands instead of  `make lint` and `make test`.
- Add CHANGELOG.md

### Fixed bugs
- Fixed synchronise state incorrectly using `GET` method.

## 1.4.0
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/33)
### Implemented enhancements
- Add Automatic Speech Recognition (ASR) profile support, optimized for user speech from varying distances.

## 1.3.0
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/31)
### Implemented enhancements
- Renamed package from avs_client to alexa_client
- Use thread timer for ping management
- Add ExpectSpeech directive

## 1.2.0
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/29)
### Implemented enhancements
- Support dialogue request id to support multi-step commands.
- Added streaming audio example

### Fixed bugs

## 1.1.0
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/28)
### Implemented enhancements
- Added support for HandlePlay directive

## 1.0.0
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/23)
### Implemented enhancements
- Handle multi-part responses
- Removed type hinting
- Added makefile

## 0.7.1
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/16)
### Implemented enhancements
- Remove requirements.txt - hard-code in setup.py instead

### Fixed bugs
- Fix incorrect callback url generation #16

## 0.6.0
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/12)
### Implemented enhancements
- Add AmazonOauth2RequestManager

## 0.5.2
[Full Changelog](https://github.com/richtier/alexa-voice-service-client/pull/6)

### Fixed bugs
- Expect 204 or 200 on synchronise device state
