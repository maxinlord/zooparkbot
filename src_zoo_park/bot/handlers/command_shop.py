from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from db import User
from sqlalchemy.ext.asyncio import AsyncSession
from tools import get_text_message

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
    await message.answer(text=await get_text_message("menu_shop"))
