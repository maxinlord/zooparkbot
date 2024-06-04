from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Photo
from tools import (
    get_text_message,
    factory_text_main_top,
    disable_not_main_window,
    bonus_for_sub_on_chat,
    bonus_for_sub_on_channel,
    bonus,
)
from bot.keyboards import (
    ik_get_bonus,
)
from bot.states import UserState
from bot.filters import GetTextButton
from config import CHANNEL_ID, CHAT_ID, CHANNEL_URL, CHAT_URL

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.main_menu, GetTextButton("bonus"), flags=flags)
async def bonus(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)
    msg = await message.answer(
        text=await get_text_message(
            "bonus",
            ctu=CHAT_URL,
            clu=CHANNEL_URL,
        ),
        reply_markup=await ik_get_bonus(
            sub_on_channel=user.sub_on_channel,
            sub_on_chat=user.sub_on_chat,
        ),
    )
    await state.update_data(active_window=msg.message_id)


@router.callback_query(UserState.main_menu, F.data == "get_bonus_chat")
async def get_bonus_chat(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    r = await query.bot.get_chat_member(chat_id=CHAT_ID, user_id=query.from_user.id)
    if r.status == "left":
        await query.answer(
            text=await get_text_message("not_subscribed_to_chat"),
            show_alert=True,
        )
        return
    user.sub_on_chat = True
    await bonus_for_sub_on_chat()
    await session.commit()
    await query.message.edit_reply_markup(
        reply_markup=await ik_get_bonus(
            sub_on_channel=user.sub_on_channel,
            sub_on_chat=user.sub_on_chat,
        )
    )


@router.callback_query(UserState.main_menu, F.data == "get_bonus_channel")
async def get_bonus_channel(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    r = await query.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=query.from_user.id)
    if r.status == "left":
        await query.answer(
            text=await get_text_message("not_subscribed_to_channel"),
            show_alert=True,
        )
        return
    user.sub_on_channel = True
    await bonus_for_sub_on_channel()
    await session.commit()
    await query.message.edit_reply_markup(
        reply_markup=await ik_get_bonus(
            sub_on_channel=user.sub_on_chat,
            sub_on_chat=user.sub_on_channel,
        )
    )


@router.callback_query(UserState.main_menu, F.data == "get_bonus")
async def get_bonus(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await bonus()