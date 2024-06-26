from aiogram import Bot
from sqlalchemy import select
from db import Game, Gamer, User
from sqlalchemy.ext.asyncio import AsyncSession
import tools


async def get_amount_gamers(session: AsyncSession, game: Game):
    gamers = await session.scalars(select(Gamer).where(Gamer.id_game == game.id_game))
    return len(gamers.all())


async def get_total_moves_game(session: AsyncSession, game: Game):
    gamers = await session.scalars(select(Gamer).where(Gamer.id_game == game.id_game))
    return sum(gamer.moves for gamer in gamers)


async def get_user_where_max_score(session: AsyncSession, game: Game):
    gamers = await session.scalars(select(Gamer).where(Gamer.id_game == game.id_game))
    gamers_sorted = sorted(gamers, key=lambda gamer: gamer.score, reverse=True)
    return gamers_sorted[0].idpk_gamer if gamers_sorted else None


async def get_first_three_places(session: AsyncSession, game: Game):
    gamers = await session.scalars(select(Gamer).where(Gamer.id_game == game.id_game))
    gamers_sorted = sorted(gamers, key=lambda gamer: gamer.score, reverse=True)
    return gamers_sorted[:3] if gamers_sorted else None


async def get_nickname_owner_game(session: AsyncSession, game: Game, bot: Bot):
    if not game.idpk_user:
        return (await bot.get_my_name()).name
    owner_game = await session.get(User, game.idpk_user)
    nickname = (
        tools.mention_html_by_username(
            username=owner_game.username, name=owner_game.nickname
        )
        if owner_game.nickname
        else owner_game.nickname
    )
    return nickname


async def get_percent_places_award(session: AsyncSession):
    percents = await tools.get_value(session=session, value_name='PERCENT_PLACES_AWARD', value_type='str')
    return [int(i.strip()) for i in percents.split(',')]
