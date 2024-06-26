import contextlib
from aiogram import Bot
from sqlalchemy import delete, select, update, and_
from db import User, RandomMerchant, Value, RequestToUnity, Game, Animal, Gamer
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.deep_linking import create_start_link
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
    get_weight_rate_bank,
    get_increase_rate_bank,
    gen_key,
    get_nickname_owner_game,
    get_first_three_places,
    get_percent_places_award,
    get_total_moves_game,
    get_amount_gamers,
)
from bot.keyboards import rk_main_menu, ik_start_created_game
import random
from datetime import datetime, timedelta
from config import dict_tr_currencys, games, CHAT_ID

petard_emoji_effect = "5046509860389126442"


async def job_sec(bot) -> None:
    pass
    # await test()
    # await add_bonus_to_users()
    # await ender_games(bot)


async def job_minute(bot) -> None:
    if datetime.now().second == 59:
        async with _sessionmaker_for_func() as session:
            await accrual_of_income(session=session)
            await update_rate_bank(session=session)
            await deleter_request_to_unity(session=session)
            await updater_mess_minigame(session=session, bot=bot)
            await ender_minigames(session=session, bot=bot)
            await session.commit()


async def verification_referrals(session: AsyncSession, bot: Bot):
    users = await session.scalars(
        select(User).where(
            and_(User.id_referrer != None, User.referral_verification == False)
        )
    )
    users = users.all()
    QUANTITY_MOVES_TO_PASS = await get_value(
        session=session, value_name="QUANTITY_MOVES_TO_PASS"
    )
    QUANTITY_RUB_TO_PASS = await get_value(
        session=session, value_name="QUANTITY_RUB_TO_PASS"
    )
    QUANTITY_USD_TO_PASS = await get_value(
        session=session, value_name="QUANTITY_USD_TO_PASS"
    )
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


async def reset_first_offer_bought(session: AsyncSession) -> None:
    await session.execute(delete(RandomMerchant))


async def add_bonus_to_users(
    session: AsyncSession,
) -> None:
    await session.execute(update(User).where(User.bonus == False).values(bonus=1))


async def update_rate_bank(session: AsyncSession):
    weight_plus, weight_minus = await get_weight_rate_bank(session=session)
    increase_plus, increase_minus = await get_increase_rate_bank(session=session)
    current_rate = await get_value(
        session=session, value_name="RATE_RUB_USD", cache_=False
    )
    sign = random.choices([1, -1], weights=[weight_plus, weight_minus])[0]
    if sign == 1:
        increase = random.choice(increase_plus)
        current_rate += increase
    elif sign == -1:
        increase = random.choice(increase_minus)
        current_rate -= increase
    MIN_RATE_RUB_USD = await get_value(session=session, value_name="MIN_RATE_RUB_USD")
    MAX_RATE_RUB_USD = await get_value(session=session, value_name="MAX_RATE_RUB_USD")
    current_rate = max(current_rate, MIN_RATE_RUB_USD)
    current_rate = min(current_rate, MAX_RATE_RUB_USD)
    await session.execute(
        update(Value).where(Value.name == "RATE_RUB_USD").values(value_int=current_rate)
    )


async def accrual_of_income(
    session: AsyncSession,
):
    users = await session.scalars(select(User))
    users = users.all()
    for user in users:
        user.rub += await income_(session=session, user=user)


async def deleter_request_to_unity(session: AsyncSession):
    await session.execute(
        delete(RequestToUnity).where(RequestToUnity.date_request_end < datetime.now())
    )


async def create_game_for_chat(session: AsyncSession, bot: Bot):
    members = await bot.get_chat_member_count(chat_id=CHAT_ID)
    award = await get_value(session=session, value_name="BANK_STORAGE", cache_=False)
    if award == 0:
        return
    SEC_TO_EXPIRE_GAME = await get_value(
        session=session, value_name="SEC_TO_EXPIRE_GAME"
    )
    game = Game(
        id_game=f"game_{gen_key(length=12)}",
        idpk_user=0,
        type_game=random.choice(list(games.keys())),
        amount_gamers=members // 2,
        amount_award=award,
        currency_award="usd",
        end_date=datetime.now() + timedelta(seconds=SEC_TO_EXPIRE_GAME),
        amount_moves=random.randint(10, 20),
    )
    session.add(game)
    await session.execute(
        update(Value).where(Value.name == "BANK_STORAGE").values(value_int=0)
    )
    award = f"{award:,d}{dict_tr_currencys.get(game.currency_award)}"
    msg = await bot.send_message(
        chat_id=CHAT_ID,
        text=await get_text_message(
            "info_game",
            nickname=(await bot.get_my_name()).name,
            game_type=game.type_game,
            amount_gamers=game.amount_gamers,
            amount_moves=game.amount_moves,
            award=award,
        ),
        disable_web_page_preview=True,
        reply_markup=await ik_start_created_game(
            link=await create_start_link(bot=bot, payload=game.id_game),
            total_gamers=game.amount_gamers,
            current_gamers=0,
        ),
    )
    game.id_mess = msg.message_id
    game.activate = True


async def ender_minigames(session: AsyncSession, bot: Bot):
    games = await session.scalars(
        select(Game).where(and_(Game.end == False, Game.last_update_mess == True))
    )
    for game in games:
        game.end = True
        if game.idpk_user == 0:
            await award_winners(bot, session, game)
        else:
            await award_winner(bot, session, game)


async def updater_mess_minigame(session: AsyncSession, bot: Bot):
    games = (
        await session.scalars(select(Game).where(Game.last_update_mess == False))
    ).all()
    for game in games:
        if game.end_date > datetime.now() and (
            await get_total_moves_game(session=session, game=game) != 0
            or await get_amount_gamers(session=session, game=game) != game.amount_gamers
        ):
            continue
        game.last_update_mess = True
        if game.idpk_user == 0:
            await gen_text_winners(bot, session, game)
        else:
            await gen_text_winner(bot, session, game)
    await session.flush()


# async def test():
#     async with _sessionmaker_for_func() as session:
#         r = await session.scalars(select(Animal))
#         for i in r.all():
#             i.code_name = i.code_name.strip()
#             i.name = i.name.strip()
#             i.description = i.description.strip()
#


async def award_winner(bot: Bot, session: AsyncSession, game: Game):
    idpk_gamer = await get_user_where_max_score(session=session, game=game)
    nickname = await get_nickname_owner_game(session=session, game=game, bot=bot)
    if not idpk_gamer:
        top_mini_game_text = await factory_text_top_mini_game(
            session=session, game=game
        )
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=top_mini_game_text,
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

    currency_translation = dict_tr_currencys[game.currency_award]
    award = f"{game.amount_award:,d}{currency_translation}"
    await bot.send_message(
        chat_id=winner.id_user,
        text=await get_text_message(
            "game_winer_message",
            award=award,
        ),
        message_effect_id=petard_emoji_effect,
        reply_markup=await rk_main_menu(),
    )
    additional_text = (
        f"\n\n{await get_text_message('game_winer', nickname=winner.nickname)}"
    )

    with contextlib.suppress(Exception):
        top_mini_game_text = await factory_text_top_mini_game(
            session=session, game=game
        )
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=top_mini_game_text,
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


async def award_winners(bot: Bot, session: AsyncSession, game: Game):
    gamers_winer: list[Gamer] = await get_first_three_places(session=session, game=game)
    nickname = await get_nickname_owner_game(session=session, game=game, bot=bot)
    if not gamers_winer:
        top_mini_game_text = await factory_text_top_mini_game(
            session=session, game=game
        )
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=top_mini_game_text,
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
    additional_text = ""
    award_percent = iter(await get_percent_places_award(session=session))
    emoji_places = iter(["🏆", "🥈", "🥉"])
    for gamer in gamers_winer:
        gamer: User = await session.get(User, gamer.idpk_gamer)
        award = game.amount_award * (next(award_percent) / 100)
        await add_to_currency(
            self=gamer,
            currency=game.currency_award,
            amount=award,
        )
        award = f"{int(award):,d}{dict_tr_currencys.get(game.currency_award)}"
        await bot.send_message(
            chat_id=gamer.id_user,
            text=await get_text_message(
                "game_winer_message",
                award=award,
            ),
            message_effect_id=petard_emoji_effect,
            reply_markup=await rk_main_menu(),
        )
        additional_text += f"\n\n{await get_text_message('game_pattern_winer', nickname=gamer.nickname, emoji_places=next(emoji_places))}"

    mess_data = (
        {"chat_id": CHAT_ID, "message_id": game.id_mess}
        if game.id_mess.isdigit()
        else {"inline_message_id": game.id_mess}
    )
    with contextlib.suppress(Exception):
        top_mini_game_text = await factory_text_top_mini_game(
            session=session, game=game
        )
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=top_mini_game_text,
                nickname=nickname,
                game_type=game.type_game,
                amount_gamers=game.amount_gamers,
                amount_moves=game.amount_moves,
                award=f"{game.amount_award:,d}{dict_tr_currencys[game.currency_award]}",
            )
            + additional_text,
            reply_markup=None,
            disable_web_page_preview=True,
            **mess_data,
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
        text_top_mini_game = await factory_text_top_mini_game(
            session=session, game=game
        )
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=text_top_mini_game,
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


async def gen_text_winners(bot: Bot, session: AsyncSession, game: Game):
    gamers_winer: list[Gamer] = await get_first_three_places(session=session, game=game)
    nickname = await get_nickname_owner_game(session=session, game=game, bot=bot)
    if not gamers_winer:
        text_top_mini_game = await factory_text_top_mini_game(
            session=session, game=game
        )
        await bot.edit_message_text(
            text=await get_text_message(
                "game_start",
                t=text_top_mini_game,
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
    additional_text = ""
    award_percent = iter(await get_percent_places_award(session=session))
    emoji_places = iter(["🏆", "🥈", "🥉"])
    for gamer in gamers_winer:
        gamer: User = await session.get(User, gamer.idpk_gamer)
        award = game.amount_award * (next(award_percent) / 100)
        award = f"{int(award):,d}{dict_tr_currencys.get(game.currency_award)}"
        await bot.send_message(
            chat_id=gamer.id_user,
            text=await get_text_message(
                "game_winer_message",
                award=award,
            ),
            message_effect_id=petard_emoji_effect,
            reply_markup=await rk_main_menu(),
        )
        additional_text += f"\n\n{await get_text_message('game_pattern_winer', nickname=gamer.nickname, emoji_places=next(emoji_places))}"
    mess_data = (
        {"chat_id": CHAT_ID, "message_id": game.id_mess}
        if game.id_mess.isdigit()
        else {"inline_message_id": game.id_mess}
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
            reply_markup=None,
            disable_web_page_preview=True,
            **mess_data,
        )


# async def test_job() -> None:
#     from db import Animal
#     async with _sessionmaker_for_func() as session:
#         r = await session.scalars(select(Animal.code_name))
#         print(r.all())
