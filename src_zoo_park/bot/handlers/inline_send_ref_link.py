import asyncio
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
from bot.keyboards import ik_start_game
from tools import get_text_message

router = Router()


@router.inline_query()
async def share_referral_link(
    inline_query: InlineQuery,
    session: AsyncSession,
    user: User | None,
):
    link = await create_start_link(bot=inline_query.bot, payload=user.idpk)
    r = InlineQueryResultArticle(
        id='ref',
        title=await get_text_message("title_inline_mess"),
        description=await get_text_message("description_inline_mess"),
        thumbnail_url="https://wepik.com/api/vector/9c37cdfd-1eed-4e23-a779-094960429bc4/preview",
        input_message_content=InputTextMessageContent(
            message_text=await get_text_message("promo_for_referrals")
        ),
        reply_markup=await ik_start_game(link=link),
    )
    await inline_query.answer(results=[r], cache_time=0)



@router.chosen_inline_result(F.result_id == "ref")
async def ref(
    chosen_result: ChosenInlineResult,
):
    return