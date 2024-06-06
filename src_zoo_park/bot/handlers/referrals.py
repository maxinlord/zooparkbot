from aiogram.types import Message, CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User
from tools import (
    get_text_message,
    get_total_number_seats,
    get_remain_seats,
    income_,
)
from bot.filters import GetTextButton
from bot.states import UserState
from bot.keyboards import ik_referrals_menu, ik_account_menu

router = Router()


@router.callback_query(UserState.main_menu, F.data == "referrals_system")
async def referrals(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    row_data = await session.scalars(
        select(User.idpk).where(User.id_referrer == user.idpk)
    )
    quantity_referrals = len(row_data.all())
    await query.message.edit_text(
        text=await get_text_message(
            "info_about_referrals",
            qr=quantity_referrals,
        ),
        reply_markup=await ik_referrals_menu(
            promo_text=await get_text_message("promo_text")
        ),
    )


@router.callback_query(UserState.main_menu, F.data == "back_ref")
async def back_to_account_menu_r(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await query.message.edit_text(
        text=await get_text_message(
            "account_info",
            nn=user.nickname,
            rub=user.rub,
            usd=user.usd,
            pawc=user.paw_coins,
            animals=user.animals,
            aviaries=user.aviaries,
            total_places=await get_total_number_seats(user.aviaries),
            remain_places=await get_remain_seats(
                aviaries=user.aviaries,
                amount_animals=user.get_total_number_animals(),
            ),
            items=user.items,
            income=await income_(user),
        ),
        reply_markup=await ik_account_menu(),
    )
