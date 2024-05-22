from aiogram.types import Message
from aiogram.utils.deep_linking import create_start_link
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User
from tools import (
    get_text_message,
)
from bot.filters import GetTextButton


router = Router()


@router.message(GetTextButton('referrals'))
async def referrals(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    row_data = await session.scalars(select(User.idpk).where(User.id_referrer == user.idpk))
    quantity_referrals = len(row_data.all())
    link = await create_start_link(bot=message.bot, payload=user.idpk)
    await message.answer(
        text=await get_text_message("info_about_referrals", link=link, qr=quantity_referrals)
    )