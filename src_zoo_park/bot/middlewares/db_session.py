from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from config import CHANNEL_ID, CHAT_ID, CHAT_SUPPORT_ID
from sqlalchemy.ext.asyncio import async_sessionmaker


class DBSessionMiddleware(BaseMiddleware):

    def __init__(self, session_pool: async_sessionmaker) -> None:
        self._session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.chat.id in [CHAT_ID, CHANNEL_ID, CHAT_SUPPORT_ID]:
            return
        async with self._session_pool() as session:
            data["session"] = session
            return await handler(event, data)
