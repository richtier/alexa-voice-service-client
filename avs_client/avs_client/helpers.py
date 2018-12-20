import collections
import json
import pprint
import time

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
    audio_attachment = None

    def __init__(self, directive, audio_attachments):
        self.directive = directive
        if self.name == 'Speak':
            self.audio_attachment = audio_attachments[self.content_id]

    @classmethod
    def from_multipart(cls, part, audio_attachments):
        directive = json.loads(part.content.decode())['directive']
        return cls(directive, audio_attachments)

    @property
    def content_id(self):
        content_id = self.directive['payload']['url'].replace('cid:', '', 1)
        return '<' + content_id + '>'

    @property
    def name(self):
        return self.directive['header']['name']

    def __repr__(self):
        return str(pprint.pprint(self.directive))


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
                yield Directive.from_multipart(part, audio_attachments)
