from aiogram.filters import CommandObject, Command
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state
from tools import (
    mention_html,
    get_text_message
)

router = Router()
flags = {"throttling_key": "default"}

@router.message(Command(commands="shop"))
async def command_reset(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    await message.answer(text=await get_text_message('menu_shop'))                                         