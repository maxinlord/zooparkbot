import contextlib
from datetime import datetime
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.deep_linking import create_start_link
from sqlalchemy import select
from db import User, Game, Gamer, Item
from tools import (
    get_text_message,
    has_special_characters_nickname,
    is_unique_nickname,
    shorten_whitespace_nickname,
    validate_command_arg,
    get_amount_gamers,
    factory_text_top_mini_game,
    get_value,
    get_nickname_owner_game,
    get_gamer,
    gamer_have_active_game,
    get_status_item,
)
from bot.states import UserState
from bot.keyboards import rk_main_menu, ik_start_created_game, ik_button_play
from game_variables import translated_currencies
from config import CHAT_ID


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
    if not game:
        await message.answer(text=await get_text_message("game_not_found"))
        return
    if game.end:
        await message.answer(text=await get_text_message("game_expired"))
        return
    if await get_gamer(session=session, id_game=id_game, idpk_gamer=user.idpk):
        await message.answer(text=await get_text_message("game_already_started"))
        return
    if await gamer_have_active_game(session=session, idpk_gamer=user.idpk):
        await message.answer(text=await get_text_message("finished_active_game"))
        return
    if game.amount_gamers == await get_amount_gamers(session=session, game=game):
        await message.answer(text=await get_text_message("game_full"))
        return
    gamer = Gamer(
        id_game=id_game,
        idpk_gamer=user.idpk,
        moves=game.amount_moves,
    )
    if await get_status_item(items=user.items, code_name_item="item_7"):
        item = await session.scalar(select(Item).where(Item.code_name == "item_7"))
        gamer.moves += item.value
    session.add(gamer)
    await session.commit()
    nickname = await get_nickname_owner_game(
        session=session, game=game, bot=message.bot
    )
    award = f"{game.amount_award:,d}{translated_currencies.get(game.currency_award)}"
    mess_data = (
        {"chat_id": CHAT_ID, "message_id": game.id_mess}
        if game.id_mess.isdigit()
        else {"inline_message_id": game.id_mess}
    )
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
            reply_markup=await ik_start_created_game(
                link=await create_start_link(bot=message.bot, payload=game.id_game),
                total_gamers=game.amount_gamers,
                current_gamers=await get_amount_gamers(session=session, game=game),
            ),
            disable_web_page_preview=True,
            **mess_data,
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
    keyboard_data = {
        "game_type": game.type_game,
        "total_moves": game.amount_moves,
        "remain_moves": gamer.moves,
    }
    if await get_status_item(items=user.items, code_name_item="item_8"):
        item = await session.scalar(select(Item).where(Item.code_name == "item_8"))
        keyboard_data["autopilot"] = True
        await state.update_data(delay_autopilot=item.value)
    await message.answer(
        text=await get_text_message("play_game", score=gamer.score),
        reply_markup=await ik_button_play(**keyboard_data),
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
    LIMIT_LENGTH_MAX = await get_value(
        session=session, value_name="NICKNAME_LENGTH_MAX"
    )
    LIMIT_LENGTH_MIN = await get_value(
        session=session, value_name="NICKNAME_LENGTH_MIN"
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
    if not await is_unique_nickname(session=session, nickname=message.text):
        await message.answer(text=await get_text_message("nickname_not_unique"))
        return
    data = await state.get_data()
    data_user = data["data_user"]
    data_user["nickname"] = await shorten_whitespace_nickname(message.text)
    data_user["date_reg"] = datetime.now()
    data_user["usd"] = await get_value(session=session, value_name="START_USD") 
    session.add(User(**data_user))
    await session.commit()
    await message.answer(
        text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
    )
    await state.set_state(UserState.main_menu)
