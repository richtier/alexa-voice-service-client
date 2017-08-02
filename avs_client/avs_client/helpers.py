import collections
import time


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
