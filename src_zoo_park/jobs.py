import contextlib
from aiogram import Bot
from sqlalchemy import delete, select, update, and_
from db import User, RandomMerchant, Value, RequestToUnity, Game, Animal
from sqlalchemy.ext.asyncio import AsyncSession
from init_db import _sessionmaker_for_func
from tools import (
    referrer_bonus,
    referral_bonus,
    get_text_message,
    get_value,
    income_,
    get_user_where_max_score,
    add_to_currency,
    factory_text_top_mini_game,
    mention_html_by_username,
)
from bot.keyboards import rk_main_menu
import random
from datetime import datetime
from config import dict_tr_currencys


async def job_sec(bot) -> None:
    await accrual_of_income()
    # await test()
    # await add_bonus_to_users()
    # await ender_games(bot)


async def job_minute(bot) -> None:
    if datetime.now().second == 59:
        await update_rate_bank()
        await deleter_request_to_unity()
        await ender_minigames(bot)
        await updater_mess_minigame(bot=bot)


async def verification_referrals(bot: Bot):
    async with _sessionmaker_for_func() as session:
        users = await session.scalars(
            select(User).where(
                and_(User.id_referrer != None, User.referral_verification == False)
            )
        )
        users = users.all()
        QUANTITY_MOVES_TO_PASS = await get_value(session=session, value_name='QUANTITY_MOVES_TO_PASS')
        QUANTITY_RUB_TO_PASS = await get_value(session=session, value_name='QUANTITY_RUB_TO_PASS')
        QUANTITY_USD_TO_PASS = await get_value(session=session, value_name='QUANTITY_USD_TO_PASS')
        for user in users:
            if user.moves < QUANTITY_MOVES_TO_PASS:
                continue
            if user.amount_expenses_rub < QUANTITY_RUB_TO_PASS:
                continue
            if user.amount_expenses_usd < QUANTITY_USD_TO_PASS:
                continue
            referrer: User = await session.get(User, user.id_referrer)
            bonus = await referrer_bonus(referrer=referrer)
            await bot.send_message(
                chat_id=referrer.id_user,
                text=await get_text_message("you_got_bonus_referrer", bonus=bonus),
            )
            bonus = await referral_bonus(session=session, referral=user)
            await bot.send_message(
                chat_id=user.id_user,
                text=await get_text_message("you_got_bonus_referral", bonus=bonus),
            )
            user.referral_verification = True
            await session.commit()


async def reset_first_offer_bought() -> None:
    async with _sessionmaker_for_func() as session:
        await session.execute(delete(RandomMerchant))
        await session.commit()


async def add_bonus_to_users() -> None:
    async with _sessionmaker_for_func() as session:
        await session.execute(update(User).where(User.bonus == False).values(bonus=1))
        await session.commit()


async def update_rate_bank():
    async with _sessionmaker_for_func() as session:
        MAX_INCREASE_TO_RATE = await get_value(session=session, value_name='MAX_INCREASE_TO_RATE')
        current_rate = await get_value(session=session, value_name='RATE_RUB_USD', cache_=False)
        current_rate += random.randint(-MAX_INCREASE_TO_RATE, MAX_INCREASE_TO_RATE)
        MIN_RATE_RUB_USD = await get_value(session=session, value_name='MIN_RATE_RUB_USD')
        MAX_RATE_RUB_USD = await get_value(session=session, value_name='MAX_RATE_RUB_USD')
        current_rate = max(current_rate, MIN_RATE_RUB_USD)
        current_rate = min(current_rate, MAX_RATE_RUB_USD)
        await session.execute(
            update(Value)
            .where(Value.name == "RATE_RUB_USD")
            .values(value_int=current_rate)
        )
        await session.commit()


async def accrual_of_income():
    async with _sessionmaker_for_func() as session:
        users = await session.scalars(select(User))
        users = users.all()
        for user in users:
            user.rub += await income_(session=session,user=user)
        await session.commit()


async def deleter_request_to_unity():
    async with _sessionmaker_for_func() as session:
        await session.execute(
            delete(RequestToUnity).where(
                RequestToUnity.date_request_end < datetime.now()
            )
        )
        await session.commit()


async def ender_minigames(bot: Bot):
    async with _sessionmaker_for_func() as session:
        games = await session.scalars(
            select(Game).where(and_(Game.end == False, Game.end_date < datetime.now()))
        )

        for game in games:
            await end_game(session, game)
            await award_winner(bot, session, game)


async def updater_mess_minigame(bot: Bot):
    async with _sessionmaker_for_func() as session:
        games = await session.scalars(
            select(Game).where(and_(Game.end == True, Game.last_update_mess == False))
        )

        for game in games:
            game.last_update_mess = True
            await gen_text_winner(bot, session, game)
            await session.commit()


async def test():
    async with _sessionmaker_for_func() as session:
        r = await session.scalars(select(Animal))
        for i in r.all():
            i.code_name = i.code_name.strip()
            i.name = i.name.strip()
            i.description = i.description.strip()
            await session.commit()


async def end_game(session: AsyncSession, game: Game):
    game.end = True
    game.last_update_mess = True
    await session.commit()


async def award_winner(bot: Bot, session: AsyncSession, game: Game):
    idpk_gamer = await get_user_where_max_score(session=session, game=game)
    owner_game = await session.get(User, game.idpk_user)
    nickname = (
        mention_html_by_username(username=owner_game.username, name=owner_game.nickname)
        if owner_game.nickname
        else owner_game.nickname
    )
    if not idpk_gamer:
        t = await factory_text_top_mini_game(session=session, game=game)
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=t,
                nickname=nickname,
                game_type=game.type_game,
                amount_gamers=game.amount_gamers,
                amount_moves=game.amount_moves,
                award=f"{game.amount_award:,d}{dict_tr_currencys[game.currency_award]}",
            )
            + await get_text_message("no_result_game"),
            inline_message_id=game.id_mess,
            reply_markup=None,
            disable_web_page_preview=True,
        )
        return
    winner = await session.get(User, idpk_gamer)
    await add_to_currency(
        self=winner,
        currency=game.currency_award,
        amount=game.amount_award,
    )
    await session.commit()
    c = dict_tr_currencys[game.currency_award]
    award = f"{game.amount_award:,d}{c}"
    await bot.send_message(
        chat_id=winner.id_user,
        text=await get_text_message(
            "game_winer_message",
            award=award,
        ),
        reply_markup=await rk_main_menu(),
    )
    additional_text = (
        f"\n\n{await get_text_message('game_winer', nickname=winner.nickname)}"
    )

    with contextlib.suppress(Exception):
        t = await factory_text_top_mini_game(session=session, game=game)
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=t,
                nickname=nickname,
                game_type=game.type_game,
                amount_gamers=game.amount_gamers,
                amount_moves=game.amount_moves,
                award=f"{game.amount_award:,d}{dict_tr_currencys[game.currency_award]}",
            )
            + additional_text,
            inline_message_id=game.id_mess,
            reply_markup=None,
            disable_web_page_preview=True,
        )


async def gen_text_winner(bot: Bot, session: AsyncSession, game: Game):
    idpk_gamer = await get_user_where_max_score(session=session, game=game)
    owner_game = await session.get(User, game.idpk_user)
    nickname = (
        mention_html_by_username(username=owner_game.username, name=owner_game.nickname)
        if owner_game.nickname
        else owner_game.nickname
    )
    if not idpk_gamer:
        t = await factory_text_top_mini_game(session=session, game=game)
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=t,
                nickname=nickname,
                game_type=game.type_game,
                amount_gamers=game.amount_gamers,
                amount_moves=game.amount_moves,
                award=f"{game.amount_award:,d}{dict_tr_currencys[game.currency_award]}",
            )
            + await get_text_message("no_result_game"),
            inline_message_id=game.id_mess,
            reply_markup=None,
            disable_web_page_preview=True,
        )
        return
    winner = await session.get(User, idpk_gamer)
    additional_text = (
        f"\n\n{await get_text_message('game_winer', nickname=winner.nickname)}"
    )

    with contextlib.suppress(Exception):
        t = await factory_text_top_mini_game(session=session, game=game)
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=t,
                nickname=nickname,
                game_type=game.type_game,
                amount_gamers=game.amount_gamers,
                amount_moves=game.amount_moves,
                award=f"{game.amount_award:,d}{dict_tr_currencys[game.currency_award]}",
            )
            + additional_text,
            inline_message_id=game.id_mess,
            reply_markup=None,
            disable_web_page_preview=True,
        )


# async def test_job() -> None:
#     from db import Animal
#     async with _sessionmaker_for_func() as session:
#         r = await session.scalars(select(Animal.code_name))
#         print(r.all())
