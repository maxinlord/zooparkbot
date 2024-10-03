import asyncio

from aiogram import Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import Message
from bot.states import AdminState
from config import ADMIN_ID
from db import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tools import get_text_message, mention_html

router = Router()
flags = {"throttling_key": "default"}


@router.message(Command(commands="m"), StateFilter(any_state))
async def command_mailing(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    if user.id_user != ADMIN_ID:
        return await message.answer("У вас нет прав")
    await state.set_state(AdminState.get_mess_mailing)
    await message.answer(text=await get_text_message("send_mess_for_mailing"))


@router.message(AdminState.get_mess_mailing)
async def get_mess_mailing(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User | None,
) -> None:
    users = await session.scalars(select(User))
    users = users.all()
    not_sended = []
    for user in users:
        try:
            await message.send_copy(chat_id=user.id_user)
        except Exception:
            not_sended.append(mention_html(user.id_user, user.username))
        await asyncio.sleep(0.5)
    amount_got_message = len(users) - len(not_sended)
    amount_not_got_message = len(not_sended)
    not_sended = ", ".join(not_sended) if not_sended else "Нет"
    await message.answer(
        text=await get_text_message(
            "mess_mailing_finish",
            amount_got_message=amount_got_message,
            amount_not_got_message=amount_not_got_message,
            not_sended=not_sended,
        )
    )
