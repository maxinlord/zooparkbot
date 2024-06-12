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
    bonus_,
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
            "bonus_info",
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
    b = await bonus_for_sub_on_chat(session=session, user=user)
    await session.commit()
    await query.message.answer(await get_text_message("subscribed_to_4at", bonus=b))
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
    b = await bonus_for_sub_on_channel(user=user)
    await session.commit()
    await query.message.answer(await get_text_message("subscribed_to_channel", bonus=b))
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
    if not user.bonus:
        await query.answer(
            text=await get_text_message("no_bonus"),
            show_alert=True,
        )
        return
    user.bonus = 0
    data_bonus = await bonus_(user=user)
    await session.commit()
    key = list(data_bonus.keys())[0]
    text = ""
    match key:
        case "rub":
            text = await get_text_message(
                "bonus_rub", rub=data_bonus[key]["rub_to_add"]
            )
        case "usd":
            text = await get_text_message(
                "bonus_usd", usd=data_bonus[key]["usd_to_add"]
            )
        case "aviary":
            text = await get_text_message(
                "bonus_aviary",
                aviary=data_bonus[key]["aviary_to_add"],
                amount=data_bonus[key]["amount_to_add"],
            )
        case "animal":
            text = await get_text_message(
                "bonus_animal",
                animal=data_bonus[key]["animal_to_add"],
                amount=data_bonus[key]["amount_to_add"],
            )
        case "item":
            text = await get_text_message(
                "bonus_item", item=data_bonus[key]["item_to_add"]
            )
    await query.message.delete_reply_markup()
    await query.message.answer(
        text=await get_text_message(
            "bonus_received",
            text=text,
        ),
    )
