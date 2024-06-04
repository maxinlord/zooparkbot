from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from tools import (
    get_text_message,
    disable_not_main_window,
    factory_text_unity_top,
)
from bot.states import UserState
from bot.filters import GetTextButton

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.unity_menu, GetTextButton("top_unity"), flags=flags)
async def unity_members(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)
    tops = await factory_text_unity_top()
    await message.answer(text=await get_text_message("unity_top_10", t=tops))
