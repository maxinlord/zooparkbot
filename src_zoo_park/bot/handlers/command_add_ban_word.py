from aiogram.filters import CommandObject, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Value
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state
from tools import income_, get_text_message, find_integers, fetch_and_parse_str_value
from bot.keyboards import ik_choice_rate_calculator
from bot.filters import CompareDataByIndex

router = Router()
flags = {"throttling_key": "default"}


@router.message(Command(commands="add"), StateFilter(any_state))
async def calculator(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
    edit: bool = False,
) -> None:
    args = command.args.split(" ")
    if not args:
        return await message.answer(text=await get_text_message("error_args"))
    patterns = await fetch_and_parse_str_value(
        session=session, value_name="pattern_ban_word", func_to_element=str
    )
    patterns.extend(args)
    str_patterns = ", ".join(patterns)
    await session.execute(
        update(Value)
        .where(Value.name == "pattern_ban_word")
        .values(value_str=str_patterns)
    )
    await session.commit()
    await message.answer(text=await get_text_message("word_to_ban_added"))
