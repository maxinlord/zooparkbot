import contextlib
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from tools import get_text_message, get_rate_bank
from bot.states import UserState
from bot.keyboards import (
    ik_bank,
    rk_exchange_bank,
    rk_main_menu,
)
from bot.filters import GetTextButton
from datetime import datetime

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.main_menu, GetTextButton("bank"), flags=flags)
async def bank(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    rate = await get_rate_bank()
    time_to_update_bank = 60 - datetime.now().second
    await message.answer(
        text=await get_text_message(
            "bank", r=rate, ub=time_to_update_bank, rub=user.rub, usd=user.usd
        ),
        reply_markup=await ik_bank(),
    )


@router.callback_query(UserState.main_menu, F.data == "update_bank")
async def update_bank(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await query.answer(cache_time=1)
    rate = await get_rate_bank()
    time_to_update_bank = 60 - datetime.now().second
    with contextlib.suppress(Exception):
        await query.message.edit_text(
            text=await get_text_message(
                "bank", r=rate, ub=time_to_update_bank, rub=user.rub, usd=user.usd
            ),
            reply_markup=await ik_bank(),
        )


@router.callback_query(UserState.main_menu, F.data == "exchange_bank")
async def exchange_bank(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    rate = await get_rate_bank()
    await state.update_data(rate=rate)
    if user.rub < rate:
        await query.answer(await get_text_message("no_money"), show_alert=True)
        return
    await query.message.delete()
    await query.message.answer(
        text=await get_text_message("enter_amount_to_exchange"),
        reply_markup=await rk_exchange_bank(),
    )
    await state.set_state(UserState.exchange_bank_step)


@router.message(UserState.exchange_bank_step, GetTextButton("exchange_all_amount"))
async def exchange_all_amount(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    if user.rub < data["rate"]:
        await message.answer(await get_text_message("no_money"))
        return
    you_change = user.rub % data["rate"]
    you_got = user.rub // data["rate"]
    user.usd += you_got
    user.rub = you_change
    await session.commit()
    await message.answer(
        await get_text_message("exchange_bank_success", you_change=you_change, you_got=you_got, rate=data['rate']),
        reply_markup=await rk_main_menu(),
    )
    await state.set_state(UserState.main_menu)


@router.message(UserState.exchange_bank_step, GetTextButton("back"))
async def back_to_bank(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await message.answer(
        text=await get_text_message("back_to_bank"), reply_markup=await rk_main_menu()
    )
    await state.set_state(UserState.main_menu)
    rate = await get_rate_bank()
    time_to_update_bank = 60 - datetime.now().second
    await message.answer(
        text=await get_text_message(
            "bank", r=rate, ub=time_to_update_bank, rub=user.rub, usd=user.usd
        ),
        reply_markup=await ik_bank(),
    )


@router.message(UserState.exchange_bank_step)
async def get_amount(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    if not message.text.isdigit():
        await message.answer(await get_text_message("enter_amount_to_exchange"))
        return
    rate = data["rate"]
    amount = int(message.text)
    if amount < rate:
        await message.answer(await get_text_message("no_money"))
        return
    if amount > user.rub:
        await message.answer(await get_text_message("no_money"))
        return
    you_change = amount - (amount % rate)
    you_got = amount // rate
    user.usd += you_got
    user.rub -= you_change
    await session.commit()
    await message.answer(
        await get_text_message(
            "exchange_bank_success", you_change=you_change, you_got=you_got, rate=rate
        ),
        reply_markup=await rk_main_menu(),
    )
    await state.set_state(UserState.main_menu)
