import contextlib
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from tools import get_text_message, get_value, get_rate, mention_html_by_username
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
    rate = await get_rate(session=session, items=user.items)
    time_to_update_bank = 60 - datetime.now().second
    await message.answer(
        text=await get_text_message(
            "bank_info", r=rate, ub=time_to_update_bank, rub=user.rub, usd=user.usd
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
    rate = await get_rate(session=session, items=user.items)
    time_to_update_bank = 60 - datetime.now().second
    with contextlib.suppress(Exception):
        await query.message.edit_text(
            text=await get_text_message(
                "bank_info", r=rate, ub=time_to_update_bank, rub=user.rub, usd=user.usd
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
    rate = await get_rate(session=session, items=user.items)
    await state.update_data(rate=rate)
    if user.rub < rate:
        await query.answer(await get_text_message("no_money"), show_alert=True)
        return
    await query.message.delete_reply_markup()
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

    you_got, remains = divmod(user.rub, data["rate"])
    you_change = you_got * data["rate"]
    user.rub = remains

    if not user.id_referrer:
        user.usd += you_got
        await message.answer(
            await get_text_message(
                "exchange_bank_success",
                you_change=you_change,
                you_got=you_got,
                rate=data["rate"],
            ),
            reply_markup=await rk_main_menu(),
        )
        await state.set_state(UserState.main_menu)
        await session.commit()
        return

    percent = await get_value(session=session, value_name="REFERRAL_PERCENT")
    referrer_got = int(you_got * (percent / 100))
    referrer = await session.get(User, user.id_referrer)
    you_got -= referrer_got
    referrer.usd += referrer_got
    user.usd += you_got

    if referrer_got > 0:
        await message.bot.send_message(
            chat_id=referrer.id_user,
            text=await get_text_message(
                "referral_bonus",
                referral=mention_html_by_username(
                    username=user.username, name=user.nickname
                ),
                amount=referrer_got,
            ),
            disable_notification=True,
            disable_web_page_preview=True,
        )
    await message.answer(
        text=await get_text_message(
            "exchange_bank_success_ref",
            you_change=you_change,
            you_got=you_got,
            referrer_got=referrer_got,
            rate=data["rate"],
        ),
        reply_markup=await rk_main_menu(),
    )
    await state.set_state(UserState.main_menu)
    await session.commit()


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
    rate = await get_rate(session=session, items=user.items)
    time_to_update_bank = 60 - datetime.now().second
    await message.answer(
        text=await get_text_message(
            "bank_info",
            r=rate,
            ub=time_to_update_bank,
            rub=user.rub,
            usd=user.usd,
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
    if not message.text.isdigit():
        await message.answer(await get_text_message("enter_amount_to_exchange"))
        return
    data = await state.get_data()
    rate = data["rate"]
    amount = int(message.text)
    if amount < rate:
        await message.answer(await get_text_message("no_money"))
        return
    if amount > user.rub:
        await message.answer(await get_text_message("no_money"))
        return

    you_got, remains = divmod(amount, data["rate"])
    you_change = you_got * data["rate"]
    # user.usd += you_got
    user.rub -= amount - remains

    if not user.id_referrer:
        user.usd += you_got
        await message.answer(
            await get_text_message(
                "exchange_bank_success",
                you_change=you_change,
                you_got=you_got,
                rate=rate,
            ),
            reply_markup=await rk_main_menu(),
        )
        await state.set_state(UserState.main_menu)
        await session.commit()
        return

    percent = await get_value(session=session, value_name="REFERRAL_PERCENT")
    referrer_got = int(you_got * (percent / 100))
    referrer = await session.get(User, user.id_referrer)
    you_got -= referrer_got
    referrer.usd += referrer_got
    user.usd += you_got

    if referrer_got > 0:
        await message.bot.send_message(
            chat_id=referrer.id_user,
            text=await get_text_message(
                "referral_bonus",
                referral=mention_html_by_username(
                    username=user.username, name=user.nickname
                ),
                amount=referrer_got,
            ),
            disable_notification=True,
            disable_web_page_preview=True,
        )
    await message.answer(
        text=await get_text_message(
            "exchange_bank_success_ref",
            you_change=you_change,
            you_got=you_got,
            referrer_got=referrer_got,
            rate=data["rate"],
        ),
        reply_markup=await rk_main_menu(),
    )
    await state.set_state(UserState.main_menu)
    await session.commit()
