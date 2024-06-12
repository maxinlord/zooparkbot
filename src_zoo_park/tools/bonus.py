import asyncio
import json
from sqlalchemy import select
from db import User, Value, Aviary, Animal, Item
import random
from config import rarities
from tools import get_value

from sqlalchemy.ext.asyncio import AsyncSession


async def referral_bonus(session: AsyncSession, referral: User):
    bonus = await get_value(session=session, value_name="REFERRAL_BONUS")
    referral.usd += bonus
    await session.commit()
    return bonus


async def referrer_bonus(session: AsyncSession, referrer: User):
    bonus = await get_value(session=session, value_name="REFERRER_BONUS")
    referrer.usd += bonus
    await session.commit()
    return bonus


async def bonus_for_sub_on_chat(session: AsyncSession, user: User):
    bonus = await get_value(session=session, value_name="SUBSCRIPTION_BONUS_ON_CHAT")
    user.usd += bonus
    await session.commit()
    return bonus


async def bonus_for_sub_on_channel(session: AsyncSession, user: User):
    bonus = await get_value(session=session, value_name="SUBSCRIPTION_BONUS_ON_CHANNEL")
    user.usd += bonus
    return bonus
