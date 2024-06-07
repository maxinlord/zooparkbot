import asyncio
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultCachedPhoto,
    InlineQueryResultPhoto,
    LinkPreviewOptions,
)
from aiogram.types import ChosenInlineResult, CallbackQuery
from aiogram import F, Router
from aiogram.utils.deep_linking import create_start_link
import random
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Photo, TransferMoney
from sqlalchemy import and_, delete, select
from bot.keyboards import ik_start_game, ik_get_money, ik_get_money_one_piece
from tools import (
    get_text_message,
    gen_key,
    add_to_currency,
    in_used,
    add_user_to_used,
    add_to_amount_expenses_currency,
    get_currency,
)
from bot.filters import CompareDataByIndex
from config import dict_tr_currencys

router = Router()


@router.inline_query(F.query.isdigit())
async def inline_send_money_one_pm(
    inline_query: InlineQuery,
    session: AsyncSession,
    user: User | None,
):
    r = InlineQueryResultArticle(
        id=str(random.randint(1, 100000)),
        title=await get_text_message("point_1"),
        description=await get_text_message("enter_currency_to_send"),
        thumbnail_url="https://www.clipartmax.com/png/full/219-2197586_organization-training-business-learning-technology-no-1-icon-png.png",
        input_message_content=InputTextMessageContent(
            message_text=await get_text_message("error_enter_currency_to_send")
        ),
    )
    await inline_query.answer(results=[r], cache_time=0)


@router.inline_query(F.query.split()[0].isdigit(), F.query.split().len() == 2)
async def inline_send_money_two_pm(
    inline_query: InlineQuery,
    session: AsyncSession,
    user: User | None,
):
    split_query = inline_query.query.split()
    if split_query[1] not in ["rub", "usd"]:
        r = InlineQueryResultArticle(
            id=str(random.randint(1, 100000)),
            title=await get_text_message("attention"),
            description=await get_text_message("enter_usd_or_rub"),
            thumbnail_url="https://avatars.yandex.net/get-music-content/2433207/64c60238.a.12011003-1/m1000x1000?webp=false",
            input_message_content=InputTextMessageContent(
                message_text=await get_text_message("error_enter_usd_or_rub")
            ),
        )
        return await inline_query.answer(results=[r], cache_time=0)
    currency = await get_currency(self=user, currency=split_query[1])
    if currency < int(split_query[0]):
        r = InlineQueryResultArticle(
            id=str(random.randint(1, 100000)),
            title=await get_text_message("attention"),
            description=await get_text_message(
                "not_enough_money_to_send", money=currency
            ),
            thumbnail_url="https://avatars.yandex.net/get-music-content/2433207/64c60238.a.12011003-1/m1000x1000?webp=false",
            input_message_content=InputTextMessageContent(
                message_text=await get_text_message("error_not_enough_money_to_send")
            ),
        )
        return await inline_query.answer(results=[r], cache_time=0)
    r = InlineQueryResultArticle(
        id=str(random.randint(1, 100000)),
        title=await get_text_message("point_2"),
        description=await get_text_message("enter_split_to_send"),
        thumbnail_url="https://cdn-ru.bitrix24.ru/b9251457/landing/7b7/7b7c7b41a9e0c33f1867fea82a8d5c08/Resurs_20_s_1x.png",
        input_message_content=InputTextMessageContent(
            message_text=await get_text_message("error_enter_split_to_send")
        ),
    )
    await inline_query.answer(results=[r], cache_time=0)


@router.inline_query(F.query.split()[0].isdigit(), F.query.split().len() == 3)
async def inline_send_money(
    inline_query: InlineQuery,
    session: AsyncSession,
    user: User | None,
):
    split_query = inline_query.query.split()
    if split_query[1] not in ["rub", "usd"]:
        r = InlineQueryResultArticle(
            id=str(random.randint(1, 100000)),
            title=await get_text_message("attention"),
            description=await get_text_message("enter_usd_or_rub"),
            thumbnail_url="https://avatars.yandex.net/get-music-content/2433207/64c60238.a.12011003-1/m1000x1000?webp=false",
            input_message_content=InputTextMessageContent(
                message_text=await get_text_message("error_enter_usd_or_rub")
            ),
        )
        return await inline_query.answer(results=[r], cache_time=0)
    d = {"sum": int(split_query[0])}
    currency = await get_currency(self=user, currency=split_query[1])
    if currency < d["sum"]:
        r = InlineQueryResultArticle(
            id=str(random.randint(1, 100000)),
            title=await get_text_message("attention"),
            description=await get_text_message(
                "not_enough_money_to_send", money=currency
            ),
            thumbnail_url="https://avatars.yandex.net/get-music-content/2433207/64c60238.a.12011003-1/m1000x1000?webp=false",
            input_message_content=InputTextMessageContent(
                message_text=await get_text_message("error_not_enough_money_to_send")
            ),
        )
        return await inline_query.answer(results=[r], cache_time=0)
    pieces = int(split_query[2])
    if pieces <= 0:
        r = InlineQueryResultArticle(
            id=str(random.randint(1, 100000)),
            title=await get_text_message("attention"),
            description=await get_text_message("amount_pieces_too_small"),
            thumbnail_url="https://avatars.yandex.net/get-music-content/2433207/64c60238.a.12011003-1/m1000x1000?webp=false",
            input_message_content=InputTextMessageContent(
                message_text=await get_text_message("error_amount_pieces_too_small")
            ),
        )
        return await inline_query.answer(results=[r], cache_time=0)
    if pieces > d["sum"] or pieces > 500:
        r = InlineQueryResultArticle(
            id=str(random.randint(1, 100000)),
            title=await get_text_message("attention"),
            description=await get_text_message("amount_pieces_too_big"),
            thumbnail_url="https://avatars.yandex.net/get-music-content/2433207/64c60238.a.12011003-1/m1000x1000?webp=false",
            input_message_content=InputTextMessageContent(
                message_text=await get_text_message("error_amount_pieces_too_big")
            ),
        )
        return await inline_query.answer(results=[r], cache_time=0)

    one_piece = d["sum"] // pieces
    key = gen_key(length=10)
    tr = TransferMoney(
        id_transfer=key,
        idpk_user=user.idpk,
        currency=split_query[1],
        one_piece_sum=one_piece,
        pieces=pieces,
    )
    session.add(tr)
    await session.commit()
    photo_url = (
        "https://imgimg.co/files/images/meshok-s-dengami/meshok-s-dengami-9.webp"
    )
    invisible_char = "&#8203;"
    d["invisible"] = f'<a href="{photo_url}">{invisible_char}</a>'
    d["nickname"] = user.nickname
    d["ps"] = pieces
    c = dict_tr_currencys[split_query[1]]
    d["currency"] = c
    one_piece = f"{one_piece:,d}{c}"
    text = (
        await get_text_message("info_about_send_money", **d)
        if pieces > 1
        else await get_text_message(
            "info_about_send_money_one_p",
            nickname=d["nickname"],
            sum=d["sum"],
            invisible=d["invisible"],
            currency=d["currency"],
        )
    )
    keyboard = (
        await ik_get_money(one_piece=one_piece, remain_pieces=pieces, idpk_tr=tr.idpk)
        if pieces > 1
        else await ik_get_money_one_piece(idpk_tr=tr.idpk)
    )
    r = InlineQueryResultArticle(
        id=f"{tr.idpk}:activate_tr",
        title=await get_text_message("point_3"),
        description=await get_text_message(
            "for_send_money_tap_on_bttn"
        ),
        thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Paris_transit_icons_-_Métro_3.svg/1200px-Paris_transit_icons_-_Métro_3.svg.png",
        input_message_content=InputTextMessageContent(
            message_text=text,
            link_preview_options=LinkPreviewOptions(show_above_text=True),
            disable_web_page_preview=False,
        ),
        reply_markup=keyboard,
    )
    await inline_query.answer(results=[r], cache_time=0)


@router.chosen_inline_result()
async def pagination_demo(chosen_result: ChosenInlineResult, session: AsyncSession):
    idpk_tr = int(chosen_result.result_id.split(":")[0])
    tr = await session.get(TransferMoney, idpk_tr)
    user = await session.scalar(
        select(User).where(User.id_user == chosen_result.from_user.id)
    )

    await add_to_currency(
        self=user,
        currency=tr.currency,
        amount=-tr.pieces * tr.one_piece_sum,
    )
    await add_to_amount_expenses_currency(
        self=user,
        currency=tr.currency,
        amount=tr.pieces * tr.one_piece_sum,
    )
    tr.status = True
    await session.flush()
    await session.execute(delete(TransferMoney).where(TransferMoney.status == False))
    await session.commit()


@router.callback_query(CompareDataByIndex("activate_tr"))
async def activate_tr(
    query: CallbackQuery,
    session: AsyncSession,
    user: User,
):
    if not user:
        await query.answer(
            text=await get_text_message("error_user_not_found"), show_alert=True
        )
        return
    idpk_tr = query.data.split(":")[0]
    tr = await session.get(TransferMoney, idpk_tr)
    if not tr:
        await query.bot.edit_message_reply_markup(
            inline_message_id=query.inline_message_id, reply_markup=None
        )
        return
    if tr.pieces == 0:
        await query.answer(text=await get_text_message("error_tr_end"), show_alert=True)
        await query.bot.edit_message_reply_markup(
            inline_message_id=query.inline_message_id, reply_markup=None
        )
        return
    if await in_used(idpk_tr=tr.idpk, idpk_user=user.idpk):
        await query.answer(
            text=await get_text_message("error_tr_already_used"), show_alert=True
        )
        return
    if tr.idpk_user == user.idpk:
        await query.answer(
            text=await get_text_message("error_tr_self"), show_alert=True
        )
        return
    await add_user_to_used(idpk_tr=tr.idpk, idpk_user=user.idpk)
    await add_to_currency(self=user, currency=tr.currency, amount=tr.one_piece_sum)
    tr.pieces -= 1
    await session.commit()
    c = dict_tr_currencys[tr.currency]
    await query.bot.send_message(
        chat_id=user.id_user,
        text=await get_text_message(
            "you_get_money",
            money=tr.one_piece_sum,
            currency=c,
        ),
    )
    keyboard = (
        await ik_get_money(
            one_piece=f"{tr.one_piece_sum:,d}{c}",
            remain_pieces=tr.pieces,
            idpk_tr=tr.idpk,
        )
        if tr.pieces > 0
        else None
    )
    await query.bot.edit_message_reply_markup(
        inline_message_id=query.inline_message_id, reply_markup=keyboard
    )
