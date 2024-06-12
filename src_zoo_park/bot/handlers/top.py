from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Photo
from tools import get_text_message, factory_text_main_top, get_photo
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
    text = await factory_text_main_top(session=session, idpk_user=user.idpk)
    await message.answer_photo(
        photo=await get_photo(session=session, photo_name="new_photo_196"),
        caption=await get_text_message("top_info", t=text),
    )
