from datetime import datetime
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Value
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from tools import (
    get_text_message,
    has_special_characters_nickname,
    is_unique_nickname,
    shorten_whitespace_nickname,
    validate_command_arg,
)
from bot.states import UserState
from bot.keyboards import rk_main_menu


router = Router()


@router.message(CommandStart(deep_link=True))
async def command_start_with_deep_link(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    state: FSMContext,
    user: User | None,
):
    if user:
        await message.answer(
            text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
        )
        return
    valid_arg = validate_command_arg(command.args)
    if not valid_arg:
        await message.answer(
            text=await get_text_message("invalid_deep_link"),
            reply_markup=None,
        )
        return
    referrer = await session.get(User, valid_arg)
    if not referrer:
        await message.answer(
            text=await get_text_message("referrer_not_exist"),
            reply_markup=None,
        )
        return
    data_user = {
        "id_user": message.from_user.id,
        "username": message.from_user.username,
        "id_referrer": referrer.idpk,
    }
    await state.set_state(UserState.start_reg)
    await state.update_data(data_user=data_user)
    await message.answer(text=await get_text_message("enter_nickname"))


@router.message(CommandStart(), StateFilter(default_state))
async def command_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User | None,
) -> None:
    if user:
        await message.answer(
            text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
        )
        return
    data_user = {
        "id_user": message.from_user.id,
        "username": message.from_user.username,
    }
    await state.set_state(UserState.start_reg)
    await state.update_data(data_user=data_user)
    await message.answer(text=await get_text_message("enter_nickname"))


@router.message(UserState.start_reg)
async def getting_nickname(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    LIMIT_LENGTH_MAX = await session.scalar(
        select(Value.value_int).where(Value.name == "NICKNAME_LENGTH_MAX")
    )
    LIMIT_LENGTH_MIN = await session.scalar(
        select(Value.value_int).where(Value.name == "NICKNAME_LENGTH_MIN")
    )
    if len(message.text) > LIMIT_LENGTH_MAX:
        await message.answer(text=await get_text_message("nickname_too_long"))
        return
    if len(message.text) < LIMIT_LENGTH_MIN:
        await message.answer(text=await get_text_message("nickname_too_short"))
        return
    if chars := await has_special_characters_nickname(message.text):
        await message.answer(
            text=await get_text_message("nickname_has_special_characters", chars=chars)
        )
        return
    if not await is_unique_nickname(message.text):
        await message.answer(text=await get_text_message("nickname_not_unique"))
        return
    data = await state.get_data()
    data_user = data["data_user"]
    data_user["nickname"] = await shorten_whitespace_nickname(message.text)
    data_user["date_reg"] = datetime.now()
    session.add(User(**data_user))
    await session.commit()
    await message.answer(
        text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
    )
    await state.clear()
