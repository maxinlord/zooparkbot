from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from tools import get_text_message
from bot.keyboards import rk_main_menu
from bot.states import UserState
from db import Game


class CheckGame(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        user = data["user"]
        state = data.get("state")
        d = await state.get_data()
        idpk_game = d.get("idpk_game")
        if idpk_game is None:
            return await handler(event, data)
        game = await session.get(Game, idpk_game)
        if game.end and data.get("raw_state") == "UserState:game":
            await state.clear()
            await state.set_state(UserState.main_menu)
            text = await get_text_message("main_menu")
            reply_markup = await rk_main_menu()
            
            if isinstance(event, Message):
                return await event.answer(text=text, reply_markup=reply_markup)
            elif isinstance(event, CallbackQuery):
                await event.message.delete()
                return await event.message.answer(text=text, reply_markup=reply_markup)
        
        return await handler(event, data)

