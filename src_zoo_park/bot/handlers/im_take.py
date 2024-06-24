import contextlib
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, MessageToSupport
from tools import (
    get_text_message,
    mention_html,
)
from bot.states import UserState
from bot.keyboards import rk_cancel, ik_im_take, rk_main_menu
from bot.filters import GetTextButton, CompareDataByIndex
from config import CHAT_SUPPORT_ID

flags = {"throttling_key": "default"}
router = Router()


@router.callback_query(CompareDataByIndex("im_take"))
async def im_take(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    idpk_message_to_support = int(query.data.split(":")[0])
    message_to_support = await session.get(MessageToSupport, idpk_message_to_support)
    await state.set_state(UserState.answer_on_question)
    msg = await query.bot.copy_message(
        chat_id=user.id_user,
        from_chat_id=CHAT_SUPPORT_ID,
        message_id=message_to_support.id_message,
    )
    await state.update_data(
        msg_id=msg.message_id,
        idpk_message_to_support=idpk_message_to_support,
        id_message_to_support=message_to_support.id_message,
    )
    await query.bot.send_message(
        chat_id=user.id_user,
        text=await get_text_message("wait_answer_on_question"),
        reply_markup=await rk_cancel(),
    )
    await query.message.edit_text(
        text=await get_text_message(
            "mess_taken",
            user=mention_html(id_user=user.id_user, name=query.from_user.full_name),
        ),
        reply_markup=None,
    )


@router.message(UserState.answer_on_question, GetTextButton("cancel"), flags=flags)
async def cancel_im_take(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    await message.bot.copy_message(
        chat_id=CHAT_SUPPORT_ID,
        from_chat_id=user.id_user,
        message_id=data["msg_id"],
        reply_markup=await ik_im_take(
            idpk_message_to_support=data["idpk_message_to_support"]
        ),
    )
    with contextlib.suppress(Exception):
        await message.bot.delete_message(
            chat_id=user.id_user, message_id=data["msg_id"]
        )
        await message.bot.delete_message(
            chat_id=CHAT_SUPPORT_ID, message_id=data["id_message_to_support"]
        )
    await state.set_state(UserState.main_menu)
    await message.answer(
        text=await get_text_message("im_take_canceled"),
        reply_markup=await rk_main_menu(),
    )
