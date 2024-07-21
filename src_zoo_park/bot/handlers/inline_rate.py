import asyncio
from datetime import datetime
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultCachedPhoto,
    InlineQueryResultPhoto,
)
from aiogram.types import ChosenInlineResult
from aiogram import F, Router
from aiogram.utils.deep_linking import create_start_link
import random
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Photo
from sqlalchemy import select
from bot.keyboards import ik_start_game, ik_update_inline_rate
from tools import get_text_message, get_value
from config import CHAT_ID

router = Router()


@router.inline_query(F.query.split()[0] == "rate")
async def inline_rate(
    inline_query: InlineQuery,
    session: AsyncSession,
    user: User | None,
):
    r = InlineQueryResultArticle(
        id=f"{random.randint(1, 100000)}:rate",
        title=await get_text_message("inline_title_rate"),
        description=await get_text_message("inline_description_rate"),
        input_message_content=InputTextMessageContent(
            message_text=await get_text_message("inline_rate_loading")
        ),
        reply_markup=await ik_update_inline_rate(inline_message_id=None),
    )
    await inline_query.answer(results=[r], cache_time=0)


@router.chosen_inline_result(F.result_id.split(":")[-1] == "rate")
async def rate_edit(chosen_result: ChosenInlineResult, session: AsyncSession):
    rate = await get_value(session=session, value_name="RATE_RUB_USD", cache_=False)
    time_to_update_bank = 60 - datetime.now().second
    bank_storage = await get_value(
        session=session, value_name="BANK_STORAGE", cache_=False
    )
    keyboard = await ik_update_inline_rate(chosen_result.inline_message_id)
    await chosen_result.bot.edit_message_text(
        text=await get_text_message(
            "inline_rate", r=rate, t=time_to_update_bank, s=bank_storage
        ),
        inline_message_id=chosen_result.inline_message_id,
        reply_markup=keyboard,
    )