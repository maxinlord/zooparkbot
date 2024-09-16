from aiogram.filters import CommandObject, Command
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state
from tools import (
    get_events_list,
    sort_events_batch
)
from config import ADMIN_ID

router = Router()
flags = {"throttling_key": "default"}


@router.message(Command(commands="h"), StateFilter(any_state))
async def command_history(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    if user.id_user != ADMIN_ID:
        return await message.answer("У вас нет прав")
    if not command.args:
        await message.answer("Не указано время")
        return
    mins = command.args
    events_list = await get_events_list(session, user.id_user)
    sev = await sort_events_batch(events_list=events_list, time=int(mins))
    if not sev:
        await message.answer(text="Нет событий")
        return
    await message.answer(text=sev)
    

