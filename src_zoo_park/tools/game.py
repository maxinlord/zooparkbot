import json
from sqlalchemy import select
from db import Text, Button, Value, Unity, User, Game, Gamer
from init_db import _sessionmaker_for_func
from tools import get_text_message, mention_html_by_username
from sqlalchemy.ext.asyncio import AsyncSession


async def get_amount_gamers(session: AsyncSession, game: Game):
    gamers = await session.scalars(select(Gamer).where(Gamer.id_game == game.id_game))
    return len(gamers.all())


async def get_total_moves(session: AsyncSession, game: Game):
    gamers = await session.scalars(select(Gamer).where(Gamer.id_game == game.id_game))
    return sum(gamer.moves for gamer in gamers)


async def get_user_where_max_score(session: AsyncSession, game: Game):
    gamers = await session.scalars(select(Gamer).where(Gamer.id_game == game.id_game))
    gamers_sorted = sorted(gamers, key=lambda gamer: gamer.score, reverse=True)
    return gamers_sorted[0].idpk_gamer if gamers_sorted else None


async def factory_text_top_mini_game(session: AsyncSession, game: Game):
    gamers = await session.scalars(select(Gamer).where(Gamer.id_game == game.id_game))
    gamers = list(gamers)
    gamers_sorted = sorted(gamers, key=lambda x: x.score, reverse=True)
    text = ""
    for counter, gamer in enumerate(gamers_sorted, start=1):
        user = await session.get(User, gamer.idpk_gamer)
        nickname = (
            mention_html_by_username(username=user.username, name=user.nickname)
            if user.nickname
            else user.nickname
        )
        text += await get_text_message(
            "pattern_place_in_top_game",
            name_=nickname,
            score=gamer.score,
            c=counter,
        )
    return text
