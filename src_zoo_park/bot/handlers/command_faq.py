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
    get_text_message,
)
from config import FAQ_URL

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
    await message.answer(text=await get_text_message("faq", link_on_faq=FAQ_URL))
