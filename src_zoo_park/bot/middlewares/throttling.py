from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from cachetools import TTLCache

THROTTLE_TIME = 0.5


class ThrottlingMiddleware(BaseMiddleware):
    caches = {"default": TTLCache(maxsize=10_000, ttl=THROTTLE_TIME)}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")
        if throttling_key is not None:
            cache = self.caches.get(throttling_key)
            if cache is not None:
                if event.chat.id in cache:
                    return
                cache[event.chat.id] = None
        return await handler(event, data)
