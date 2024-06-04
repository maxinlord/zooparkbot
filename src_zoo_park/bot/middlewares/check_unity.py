from datetime import datetime
from pprint import pprint
from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tools import get_text_message
from bot.keyboards import rk_main_menu
from bot.states import UserState
from db import User, BlackList


class CheckUnity(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        user = data["user"]
        if (
            user
            and not user.current_unity
            and data.get("raw_state") == "UserState:unity_menu"
        ):
            state = data.get("state")
            if isinstance(event, Message):
                await state.set_state(UserState.main_menu)
                return await event.answer(
                    text=await get_text_message("main_menu"),
                    reply_markup=await rk_main_menu(),
                )
            elif isinstance(event, CallbackQuery):
                await state.set_state(UserState.main_menu)
                await event.message.delete()
                return await event.message.answer(
                    text=await get_text_message("main_menu"),
                    reply_markup=await rk_main_menu(),
                )
        return await handler(event, data)
