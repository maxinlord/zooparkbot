from cachetools import cached, TTLCache

text_cache = TTLCache(maxsize=500, ttl=5000)
button_cache = TTLCache(maxsize=500, ttl=5000)
value_cache = TTLCache(maxsize=500, ttl=5000)
photo_cache = TTLCache(maxsize=100, ttl=5000)