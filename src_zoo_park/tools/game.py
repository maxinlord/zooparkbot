from sqlalchemy import select
from db import Game, Gamer
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
