import contextlib
from datetime import datetime
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.deep_linking import create_start_link
from sqlalchemy import and_, select
from db import User, Value, Game, Gamer
from tools import (
    get_text_message,
    has_special_characters_nickname,
    is_unique_nickname,
    shorten_whitespace_nickname,
    validate_command_arg,
    get_amount_gamers,
    factory_text_top_mini_game,
    mention_html_by_username,
)
from bot.states import UserState
from bot.keyboards import rk_main_menu, ik_start_created_game, ik_button_play
from config import dict_tr_currencys


router = Router()


@router.message(CommandStart(deep_link=True), F.text.contains("game_"))
async def command_start_game(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    state: FSMContext,
    user: User | None,
):
    if not user:
        data_user = {
            "id_user": message.from_user.id,
            "username": message.from_user.username,
        }
        await state.set_state(UserState.start_reg_step)
        await state.update_data(data_user=data_user)
        await message.answer(text=await get_text_message("enter_nickname"))
        return
    user.username = message.from_user.username
    id_game = command.args
    game = await session.scalar(select(Game).where(Game.id_game == id_game))
    data = await state.get_data()
    if not game:
        await message.answer(text=await get_text_message("game_not_found"))
        return
    if await session.scalar(
        select(Gamer).where(
            and_(Gamer.id_game == id_game, Gamer.idpk_gamer == user.idpk)
        )
    ):
        await message.answer(text=await get_text_message("game_already_started"))
        return
    if data.get("idpk_game"):
        await message.answer(text=await get_text_message("finished_active_game"))
        return
    if game.end:
        await message.answer(text=await get_text_message("game_expired"))
        return
    if game.amount_gamers == await get_amount_gamers(session=session, game=game):
        await message.answer(text=await get_text_message("game_full"))
        return
    gamer = Gamer(
        id_game=id_game,
        idpk_gamer=user.idpk,
        moves=game.amount_moves,
    )
    session.add(gamer)
    await session.commit()
    owner_game = await session.get(User, game.idpk_user)
    nickname = (
        mention_html_by_username(username=owner_game.username, name=owner_game.nickname)
        if owner_game.nickname
        else owner_game.nickname
    )
    c = dict_tr_currencys[game.currency_award]
    award = f"{game.amount_award:,d}{c}"
    with contextlib.suppress(Exception):
        t = await factory_text_top_mini_game(session=session, game=game)
        await message.bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=t,
                nickname=nickname,
                game_type=game.type_game,
                amount_gamers=game.amount_gamers,
                amount_moves=game.amount_moves,
                award=award,
            ),
            inline_message_id=game.id_mess,
            reply_markup=await ik_start_created_game(
                link=await create_start_link(bot=message.bot, payload=game.id_game),
                total_gamers=game.amount_gamers,
                current_gamers=await get_amount_gamers(session=session, game=game),
            ),
            disable_web_page_preview=True,
        )
    await state.set_state(UserState.game)
    await state.update_data(
        idpk_game=game.idpk,
        nickname=nickname,
        award=award,
        type_game=game.type_game,
        amount_gamers=game.amount_gamers,
        amount_moves=game.amount_moves,
    )
    await message.answer(
        text=await get_text_message("begin_game"), reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        text=await get_text_message("play_game", score=gamer.score),
        reply_markup=await ik_button_play(
            game_type=game.type_game,
            total_moves=game.amount_moves,
            remain_moves=gamer.moves,
        ),
    )


@router.message(CommandStart(deep_link=True))
async def command_start_with_deep_link(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    state: FSMContext,
    user: User | None,
):
    if user:
        await message.answer(
            text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
        )
        return
    valid_arg = validate_command_arg(command.args)
    if not valid_arg:
        await message.answer(
            text=await get_text_message("invalid_deep_link"),
            reply_markup=None,
        )
        return
    referrer = await session.get(User, valid_arg)
    if not referrer:
        await message.answer(
            text=await get_text_message("referrer_not_exist"),
            reply_markup=None,
        )
        return
    data_user = {
        "id_user": message.from_user.id,
        "username": message.from_user.username,
        "id_referrer": referrer.idpk,
    }
    await state.set_state(UserState.start_reg_step)
    await state.update_data(data_user=data_user)
    await message.answer(text=await get_text_message("enter_nickname"))


@router.message(CommandStart())
async def command_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User | None,
) -> None:
    if user:
        await message.answer(
            text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
        )
        await state.set_state(UserState.main_menu)
        return
    data_user = {
        "id_user": message.from_user.id,
        "username": message.from_user.username,
    }
    await state.set_state(UserState.start_reg_step)
    await state.update_data(data_user=data_user)
    await message.answer(text=await get_text_message("enter_nickname"))


@router.message(UserState.start_reg_step)
async def getting_nickname(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    LIMIT_LENGTH_MAX = await session.scalar(
        select(Value.value_int).where(Value.name == "NICKNAME_LENGTH_MAX")
    )
    LIMIT_LENGTH_MIN = await session.scalar(
        select(Value.value_int).where(Value.name == "NICKNAME_LENGTH_MIN")
    )
    if len(message.text) > LIMIT_LENGTH_MAX:
        await message.answer(text=await get_text_message("nickname_too_long"))
        return
    if len(message.text) < LIMIT_LENGTH_MIN:
        await message.answer(text=await get_text_message("nickname_too_short"))
        return
    if chars := await has_special_characters_nickname(message.text):
        await message.answer(
            text=await get_text_message("nickname_has_special_characters", chars=chars)
        )
        return
    if not await is_unique_nickname(message.text):
        await message.answer(text=await get_text_message("nickname_not_unique"))
        return
    data = await state.get_data()
    data_user = data["data_user"]
    data_user["nickname"] = await shorten_whitespace_nickname(message.text)
    data_user["date_reg"] = datetime.now()
    session.add(User(**data_user))
    await session.commit()
    await message.answer(
        text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
    )
    await state.set_state(UserState.main_menu)
