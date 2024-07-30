import contextlib
from datetime import datetime
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import F, Router
from tools import get_text_message
from sqlalchemy.ext.asyncio import AsyncSession
from db import Photo, User
from aiogram.fsm.context import FSMContext
from bot.states import UserState
from tools import get_text_message, get_value
from bot.keyboards import ik_start_game, ik_update_inline_rate
from typing import Any
from bot.filters import CompareDataByIndex
from aiogram.filters import CommandObject, Command
from aiogram.filters import StateFilter

router = Router()
flags = {"throttling_key": "default"}

from aiogram.fsm.state import any_state

@router.message(
    Command(commands="reset"),
    StateFilter(any_state),
    flags=flags,
)
async def reset(
    message: Message,
    state: FSMContext,
):
    await state.clear()
    await message.answer(text=await get_text_message('reset_done'))

@router.message(F.content_type == "photo")
async def photo_catch(message: Message, session: AsyncSession) -> None:
    photo_id = message.photo[-1].file_id
    session.add(Photo(name=f"new_photo_{message.message_id}", photo_id=photo_id))
    await session.commit()
    await message.answer(text=await get_text_message("photo_saved"))


@router.message()
async def any_unknown_message(message: Message, state: FSMContext) -> None:
    await message.answer(text=await get_text_message("answer_on_unknown_message"))
    # print(message.effect_id)


# @router.channel_post()
# async def any_unknown_channel_post(message: Message) -> None:
#     print(message.chat.id)

# @router.message(F.text == 'test')
# async def test(message: Message, session: AsyncSession) -> None:
#     await message.answer_game()

@router.callback_query(CompareDataByIndex('update_inline_rate'))
async def update_inline_rate(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
) -> None:
    rate = await get_value(session=session, value_name="RATE_RUB_USD", cache_=False)
    time_to_update_bank = 60 - datetime.now().second
    bank_storage = await get_value(
        session=session, value_name="BANK_STORAGE", cache_=False
    )
    inline_message_id = query.data.split(":")[0]
    with contextlib.suppress(Exception):
        await query.bot.edit_message_text(
            inline_message_id=inline_message_id,
            text=await get_text_message(
                "inline_rate",
                r=rate,
                t=time_to_update_bank,
                s=bank_storage,
            ),
            reply_markup=await ik_update_inline_rate(inline_message_id)
        )


@router.callback_query()
async def any_unknown_callback(query: CallbackQuery) -> None:
    await query.message.edit_reply_markup(reply_markup=None)
