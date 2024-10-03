from aiogram import Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import LinkPreviewOptions, Message
from config import FAQ_URL
from db import User
from sqlalchemy.ext.asyncio import AsyncSession
from tools import (
    get_text_message,
)

router = Router()
flags = {"throttling_key": "default"}


@router.message(
    Command(commands="faq"),
    StateFilter(any_state),
    flags=flags,
)
async def faq(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
):
    await message.answer(
        text=await get_text_message("faq", link_on_faq=FAQ_URL),
        link_preview_options=LinkPreviewOptions(show_above_text=True),
    )
