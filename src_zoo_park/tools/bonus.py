import asyncio
import json
from sqlalchemy import select
from db import User, Value, Aviary, Animal, Item
from init_db import _sessionmaker_for_func
import random
from config import rarities

async def referral_bonus(referral: User):
    async with _sessionmaker_for_func() as session:
        bonus = await session.scalar(
            select(Value.value_int).where(Value.name == "REFERRAL_BONUS")
        )
        referral.usd += bonus
        await session.commit()
        return bonus


async def referrer_bonus(referrer: User):
    async with _sessionmaker_for_func() as session:
        bonus = await session.scalar(
            select(Value.value_int).where(Value.name == "REFERRER_BONUS")
        )
        referrer.usd += bonus
        await session.commit()
        return bonus


async def bonus_for_sub_on_chat(user: User):
    async with _sessionmaker_for_func() as session:
        bonus = await session.scalar(
            select(Value.value_int).where(Value.name == "SUBSCRIPTION_BONUS_ON_CHAT")
        )
        user.usd += bonus
        await session.commit()


async def bonus_for_sub_on_channel(user: User):
    async with _sessionmaker_for_func() as session:
        bonus = await session.scalar(
            select(Value.value_int).where(Value.name == "SUBSCRIPTION_BONUS_ON_CHANNEL")
        )
        user.usd += bonus
        return bonus


