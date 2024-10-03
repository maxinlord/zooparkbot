from aiogram import Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import Message
from db import User
from sqlalchemy.ext.asyncio import AsyncSession
from tools import (
    get_photo,
    get_text_message,
)

router = Router()
flags = {"throttling_key": "default"}


@router.message(Command(commands="p"), StateFilter(any_state))
async def photo_view(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    if not command.args:
        await message.answer(text=await get_text_message("error_args"))
        return
    try:
        photo = await get_photo(session=session, photo_name=command.args.strip())
    except Exception:
        await message.answer(text=await get_text_message("error_photo"))
        return
    await message.answer_photo(photo=photo)
