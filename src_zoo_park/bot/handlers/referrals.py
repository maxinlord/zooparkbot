from aiogram.types import CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from tools import (
    get_text_message,
    get_referrals,
    get_value,
    get_verify_referrals
)
from bot.states import UserState
from bot.keyboards import ik_referrals_menu

router = Router()


@router.callback_query(UserState.main_menu, F.data == "referrals_system")
async def referrals(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    quantity_referrals = await get_referrals(session=session, user=user)
    quantity_verify_referrals = await get_verify_referrals(session=session, user=user)
    received_bonus = bonus * quantity_verify_referrals
    bonus = await get_value(session=session, value_name="REFERRER_BONUS")
    await query.message.edit_text(
        text=await get_text_message(
            "info_about_referrals",
            qr=quantity_referrals,
            qvr=quantity_verify_referrals,
            rb=received_bonus,
            b=bonus
        ),
        reply_markup=await ik_referrals_menu(
            promo_text=await get_text_message("promo_text")
        ),
    )