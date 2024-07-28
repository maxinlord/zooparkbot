import json
from datetime import datetime
from typing import Callable, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from tools import get_value


class RegMove(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user: User = data["user"]
        if user:
            session: AsyncSession = data["session"]
            LIMIT_ON_WRITE_MOVES = await get_value(
                session=session, value_name="LIMIT_ON_WRITE_MOVES"
            )
            decoded_dict: dict = json.loads(user.history_moves)
            key = datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")
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
