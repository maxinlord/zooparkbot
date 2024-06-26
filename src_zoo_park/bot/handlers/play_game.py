import contextlib
from aiogram.types import (
    CallbackQuery,
)
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from aiogram.utils.deep_linking import create_start_link
from db import User, Game, Gamer
from tools import (
    get_text_message,
    get_amount_gamers,
    factory_text_top_mini_game,
    get_user_where_max_score,
    get_first_three_places,
    add_to_currency,
    get_percent_places_award,
)
from bot.states import UserState
from bot.keyboards import (
    rk_zoomarket_menu,
    rk_main_menu,
    ik_button_play,
    ik_start_created_game,
)
import asyncio
from config import dict_tr_currencys, CHAT_ID

router = Router()
petard_emoji_effect = "5046509860389126442"


async def handle_game_end(
    query: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await query.message.answer(
        text=await get_text_message("game_end"), reply_markup=await rk_main_menu()
    )
    await state.clear()
    await state.set_state(UserState.main_menu)


@router.callback_query(UserState.game, F.data == "dice")
async def play_game(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    game = await session.get(Game, data["idpk_game"])
    await query.message.delete_reply_markup()
    msg = await query.message.answer_dice(emoji=game.type_game)
    value_dice = msg.dice.value
    await asyncio.sleep(4)

    gamer = await session.scalar(
        select(Gamer).where(
            and_(Gamer.idpk_gamer == user.idpk, Gamer.id_game == game.id_game)
        )
    )
    gamer.score += value_dice
    gamer.moves -= 1

    await session.flush()

    if gamer.moves == 0:
        await query.message.answer(
            text=await get_text_message("you_got", value_dice=value_dice)
        )
        await query.message.answer(
            text=await get_text_message(
                "play_game",
                score=gamer.score,
            )
        )
        await handle_game_end(query, state, session)
    else:
        await query.message.answer(
            text=await get_text_message("you_got", value_dice=value_dice)
        )
        await query.message.answer(
            text=await get_text_message(
                "play_game",
                score=gamer.score,
            ),
            reply_markup=await ik_button_play(
                game_type=game.type_game,
                total_moves=game.amount_moves,
                remain_moves=gamer.moves,
            ),
        )

    mess_data = (
        {"chat_id": CHAT_ID, "message_id": game.id_mess}
        if game.id_mess.isdigit()
        else {"inline_message_id": game.id_mess}
    )
    with contextlib.suppress(Exception):
        t = await factory_text_top_mini_game(session=session, game=game)
        await query.message.bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=t,
                nickname=data["nickname"],
                game_type=data["type_game"],
                amount_gamers=data["amount_gamers"],
                amount_moves=data["amount_moves"],
                award=data["award"],
            ),
            reply_markup=await ik_start_created_game(
                link=await create_start_link(bot=query.bot, payload=game.id_game),
                total_gamers=data["amount_gamers"],
                current_gamers=await get_amount_gamers(session=session, game=game),
            ),
            disable_web_page_preview=True,
            **mess_data,
        )
    await session.commit()
