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
    get_total_moves,
    get_user_where_max_score,
    add_to_currency,
)
from bot.states import UserState
from bot.keyboards import (
    rk_zoomarket_menu,
    rk_main_menu,
    ik_button_play,
    ik_start_created_game,
)
import asyncio


router = Router()


async def handle_game_end(
    query: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await query.message.answer(
        text=await get_text_message("game_end"), reply_markup=await rk_main_menu()
    )
    await state.clear()
    await state.set_state(UserState.main_menu)


async def handle_game_winner(query, session, game, data):
    idpk_winer = await get_user_where_max_score(session=session, game=game)
    winer = await session.get(User, idpk_winer)
    additional_text = (
        f"\n\n{await get_text_message('game_winer', nickname=winer.nickname)}"
    )
    await add_to_currency(
        self=winer,
        currency=game.currency_award,
        amount=game.amount_award,
    )
    await query.bot.send_message(
        chat_id=winer.id_user,
        text=await get_text_message(
            "game_winer_message",
            award=data["award"],
        ),
    )
    return additional_text


@router.callback_query(UserState.game, F.data == "dice")
async def buy_one_of_offer(
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
    await session.commit()
    if gamer.moves == 0:
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

    additional_text = ""
    flag_end_game = False
    if (
        await get_amount_gamers(session=session, game=game) == game.amount_gamers
        and await get_total_moves(session=session, game=game) == 0
    ):
        additional_text = await handle_game_winner(query, session, game, data)
        game.end = True
        flag_end_game = True
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
            )
            + additional_text,
            inline_message_id=game.id_mess,
            reply_markup=await ik_start_created_game(
                link=await create_start_link(bot=query.bot, payload=game.id_game),
                total_gamers=data["amount_gamers"],
                current_gamers=await get_amount_gamers(session=session, game=game),
            ),
            disable_web_page_preview=True,
        )
        if flag_end_game:
            game.last_update_mess = flag_end_game
    await session.commit()
