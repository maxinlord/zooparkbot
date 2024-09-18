from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from tools import (
    get_text_message,
    disable_not_main_window,
    bonus_for_sub_on_chat,
    bonus_for_sub_on_channel,
    get_bonus,
    apply_bonus,
    DataBonus,
    ft_bonus_info,
    get_value_prop_from_iai,
)
from bot.keyboards import ik_get_bonus, ik_confirm_or_change_bonus
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
    b = await bonus_for_sub_on_channel(session=session, user=user)
    await session.commit()
    await query.message.answer(await get_text_message("subscribed_to_channel", bonus=b))
    await query.message.edit_reply_markup(
        reply_markup=await ik_get_bonus(
            sub_on_channel=user.sub_on_chat,
            sub_on_chat=user.sub_on_channel,
        )
    )


@router.callback_query(UserState.main_menu, F.data == "get_bonus")
async def get_daily_bonus(
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
    data_bonus = await get_bonus(session=session, user=user)
    text = await ft_bonus_info(data_bonus=data_bonus)
    mess_data = {"text": text}
    data = await state.get_data()
    if (
        v := get_value_prop_from_iai(
            info_about_items=user.info_about_items, name_prop="bonus_changer"
        )
    ) and data.get("number_attempts_item", 1) > 0:
        await state.update_data(
            number_attempts_item=v,
            bonus_type=data_bonus.bonus_type,
            result_func=data_bonus.result_func,
        )
        mess_data["reply_markup"] = await ik_confirm_or_change_bonus(
            number_attempts_item=v
        )
    else:
        await state.clear()
        await state.set_state(UserState.main_menu)
        user.bonus -= 1
        await apply_bonus(session=session, user=user, data_bonus=data_bonus)
    await session.commit()
    await query.message.delete_reply_markup()
    await query.message.answer(
        **mess_data,
    )


@router.callback_query(UserState.main_menu, F.data == "confirm_bonus")
async def confirm_bonus(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    user.bonus -= 1
    data_bonus = DataBonus(
        bonus_type=data.get("bonus_type"),
        result_func=data.get("result_func"),
    )
    await apply_bonus(session=session, user=user, data_bonus=data_bonus)
    await state.clear()
    await state.set_state(UserState.main_menu)
    await session.commit()
    await query.message.delete_reply_markup()


@router.callback_query(UserState.main_menu, F.data == "change_bonus")
async def change_bonus(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    number_attempts_item = data.get("number_attempts_item", 1) - 1
    data_bonus = await get_bonus(session=session, user=user)
    text = await ft_bonus_info(data_bonus=data_bonus)
    mess_data = {"text": text}
    if number_attempts_item > 0:
        _ = await state.update_data(
            bonus_type=data_bonus.bonus_type,
            result_func=data_bonus.result_func,
            number_attempts_item=number_attempts_item,
        )
        mess_data["reply_markup"] = await ik_confirm_or_change_bonus(
            number_attempts_item=number_attempts_item
        )
    else:
        user.bonus -= 1
        await state.clear()
        await state.set_state(UserState.main_menu)
        await apply_bonus(session=session, user=user, data_bonus=data_bonus)
        await session.commit()
    await query.message.edit_text(
        **mess_data,
    )
