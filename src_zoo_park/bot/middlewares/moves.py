import json
from datetime import datetime
from typing import Callable, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from db import User


class RegMove(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user: User = data["user"]
        if user:
            LIMIT_ON_WRITE_MOVES = 20
            session: AsyncSession = data["session"]
            decoded_dict: dict = json.loads(user.history_moves)
            key = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            decoded_dict[key] = event.text
            if len(decoded_dict) > LIMIT_ON_WRITE_MOVES:
                # Преобразуем словарь в список кортежей
                items = list(decoded_dict.items())
                # Удаляем первый элемент
                first_item = items.pop(0)
                # Преобразуем список кортежей обратно в словарь
                decoded_dict = dict(items)
            user.history_moves = json.dumps(decoded_dict, ensure_ascii=False)
            user.moves += 1
            await session.commit()
        return await handler(event, data)
