from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message
from bot.filters import GetTextButton
from bot.keyboards import ik_choice_type_top
from bot.states import UserState
from db import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tools import (
    factory_text_main_top,
    factory_text_main_top_by_animals,
    factory_text_main_top_by_money,
    factory_text_main_top_by_referrals,
    get_plot,
    get_text_message,
)

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
    filename = await get_plot(session=session, type="income")
    amount_gamers = len((await session.scalars(select(User.idpk))).all())
    if filename:
        await message.answer_photo(
            photo=FSInputFile(path=filename),
            caption=await get_text_message("top_info", t=text, ag=amount_gamers),
            reply_markup=await ik_choice_type_top(chosen="top_income"),
        )
    else:
        await message.answer(
            text=await get_text_message("no_top"),
        )


@router.callback_query(UserState.main_menu, F.data == "top_money")
async def top_money(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    text = await factory_text_main_top_by_money(session=session, idpk_user=user.idpk)
    filename = await get_plot(session=session, type="money")
    amount_gamers = len((await session.scalars(select(User.idpk))).all())
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(path=filename),
            caption=await get_text_message("top_info", t=text, ag=amount_gamers),
        ),
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
    filename = await get_plot(session=session, type="income")
    amount_gamers = len((await session.scalars(select(User.idpk))).all())
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(path=filename),
            caption=await get_text_message("top_info", t=text, ag=amount_gamers),
        ),
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
    filename = await get_plot(session=session, type="animals")
    amount_gamers = len((await session.scalars(select(User.idpk))).all())
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(path=filename),
            caption=await get_text_message("top_info", t=text, ag=amount_gamers),
        ),
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
    filename = await get_plot(session=session, type="referrals")
    amount_gamers = len((await session.scalars(select(User.idpk))).all())
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(path=filename),
            caption=await get_text_message("top_info", t=text, ag=amount_gamers),
        ),
        reply_markup=await ik_choice_type_top(chosen="top_referrals"),
    )
