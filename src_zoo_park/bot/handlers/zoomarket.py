from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from tools import (
    get_text_message,
)
from bot.keyboards import rk_zoomarket_menu
from bot.filters import GetTextButton


router = Router()


@router.message(GetTextButton("zoomarket"))
async def zoomarket(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await message.answer(
        text=await get_text_message("zoomarket"), reply_markup=await rk_zoomarket_menu()
    )
