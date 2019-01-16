import collections
import json
import pprint
import time
import uuid

import requests
from requests_toolbelt import MultipartDecoder


Cache = collections.namedtuple('Cache', ['value', 'time'])


class expiring_memo(object):
    caches = {}

    def __init__(self, ttl):
        self.ttl = ttl

    def __call__(self, func):
        def inner(target, *args, **kwargs):
            cache_id = id(target)
            cache = self.caches.get(cache_id)
            now = time.time()
            if not cache or (now - cache.time) > self.ttl:
                value = func(target, *args)
                self.caches[cache_id] = cache = Cache(value=value, time=now)
            return cache.value
        return inner


class Directive:

    def __init__(self, content):
        self.directive = content

    @staticmethod
    def parse_multipart(part):
        return json.loads(part.content.decode())['directive']

    @classmethod
    def from_multipart(cls, part):
        content = cls.parse_multipart(part)
        return cls(content)

    @property
    def name(self):
        return self.directive['header']['name']

    def __repr__(self):
        return str(pprint.pprint(self.directive))


class SpeakDirective(Directive):
    def __init__(self, audio_attachment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_attachment = audio_attachment

    @staticmethod
    def get_content_id(directive):
        content_id = directive['payload']['url'].replace('cid:', '', 1)
        return '<' + content_id + '>'

    @classmethod
    def from_multipart(cls, part, audio_attachments):
        content = cls.parse_multipart(part)
        return cls(
            content=content,
            audio_attachment=audio_attachments[cls.get_content_id(content)]
        )


class PlayDirective(Directive):
    def __init__(self, audio_attachment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_attachment = audio_attachment

    @staticmethod
    def get_url(directive):
        return directive['payload']['audioItem']['stream']['url']

    @classmethod
    def from_multipart(cls, part):
        content = cls.parse_multipart(part)
        response = requests.get(cls.get_url(content))
        return cls(
            content=content,
            audio_attachment=response.content
        )


class ExpectSpeechDirective(Directive):

    @property
    def dialog_request_id(self):
        return self.directive['header']['dialogRequestId']


class AVSMultipartDecoder:

    def __init__(self, response):
        parsed_response = MultipartDecoder(
            response.read(),
            response.headers['content-type'][0].decode()
        )
        self.parts = parsed_response.parts

    @property
    def audio_attachments(self):
        attachments = {}
        for part in self.parts:
            if part.headers[b'Content-Type'] == b'application/octet-stream':
                content_id = part.headers[b'Content-ID'].decode()
                attachments[content_id] = part.content
        return attachments

    @property
    def directives(self):
        audio_attachments = self.audio_attachments
        for part in self.parts:
            if part.headers[b'Content-Type'].startswith(b'application/json'):
                name = Directive.parse_multipart(part)['header']['name']
                if name == 'Speak':
                    yield SpeakDirective.from_multipart(
                        part=part, audio_attachments=audio_attachments
                    )
                elif name == 'Play':
                    yield PlayDirective.from_multipart(part)
                elif name == 'ExpectSpeech':
                    yield ExpectSpeechDirective.from_multipart(part)
                else:
                    yield Directive.from_multipart(part)


def generate_unique_id():
    return str(uuid.uuid4())
