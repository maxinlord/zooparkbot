from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.keyboards import ik_referrals_menu
from bot.states import UserState
from db import User
from sqlalchemy.ext.asyncio import AsyncSession
from tools import get_referrals, get_text_message, get_value, get_verify_referrals

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
    bonus = await get_value(session=session, value_name="REFERRER_BONUS")
    received_bonus = bonus * quantity_verify_referrals
    await query.message.edit_text(
        text=await get_text_message(
            "info_about_referrals",
            qr=quantity_referrals,
            qvr=quantity_verify_referrals,
            rb=received_bonus,
            b=bonus,
        ),
        reply_markup=await ik_referrals_menu(
            promo_text=await get_text_message("promo_text")
        ),
    )
