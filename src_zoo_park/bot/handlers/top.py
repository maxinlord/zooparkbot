from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Photo
from tools import (
    get_text_message,
    factory_text_main_top,
    get_photo,
    factory_text_main_top_by_money,
    factory_text_main_top_by_animals,
    factory_text_main_top_by_referrals,
)
from bot.states import UserState
from bot.filters import GetTextButton
from bot.keyboards import ik_choice_type_top

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.main_menu, GetTextButton("top"), flags=flags)
async def main_top(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    text = await factory_text_main_top(session=session, idpk_user=user.idpk)
    await message.answer_photo(
        photo=await get_photo(session=session, photo_name="plug_photo"),
        caption=await get_text_message("top_info", t=text),
        reply_markup=await ik_choice_type_top(chosen="top_income"),
    )


@router.callback_query(UserState.main_menu, F.data == "top_money")
async def top_money(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    text = await factory_text_main_top_by_money(session=session, idpk_user=user.idpk)
    await query.message.edit_caption(
        caption=await get_text_message("top_info", t=text),
        reply_markup=await ik_choice_type_top(chosen="top_money"),
    )


@router.callback_query(UserState.main_menu, F.data == "top_income")
async def top_income(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    text = await factory_text_main_top(session=session, idpk_user=user.idpk)
    await query.message.edit_caption(
        caption=await get_text_message("top_info", t=text),
        reply_markup=await ik_choice_type_top(chosen="top_income"),
    )


@router.callback_query(UserState.main_menu, F.data == "top_animals")
async def top_animals(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    text = await factory_text_main_top_by_animals(session=session, idpk_user=user.idpk)
    await query.message.edit_caption(
        caption=await get_text_message("top_info", t=text),
        reply_markup=await ik_choice_type_top(chosen="top_animals"),
    )


@router.callback_query(UserState.main_menu, F.data == "top_referrals")
async def top_referrals(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    text = await factory_text_main_top_by_referrals(
        session=session, idpk_user=user.idpk
    )
    await query.message.edit_caption(
        caption=await get_text_message("top_info", t=text),
        reply_markup=await ik_choice_type_top(chosen="top_referrals"),
    )
