from datetime import datetime
from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import User, BlackList


class CheckUser(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        if await session.scalar(
            select(BlackList).where(BlackList.id_user == event.from_user.id)
        ):
            return
        user = await session.scalar(
            select(User).where(User.id_user == event.from_user.id)
        )
        data["user"] = user
        return await handler(event, data)
