from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Photo
from tools import (
    get_text_message,
    factory_text_main_top,
)
from bot.states import UserState
from bot.filters import GetTextButton

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.main_menu, GetTextButton("top"), flags=flags)
async def main_top(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    text = await factory_text_main_top(user.idpk)
    await message.answer_photo(
        photo=await session.scalar(
            select(Photo.photo_id).where(Photo.name == "plug_photo")
        ),
        caption=await get_text_message("top", t=text),
    )
