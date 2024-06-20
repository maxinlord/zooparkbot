from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Value, Aviary, Item
from sqlalchemy import select, update
import random
import tools
import json


async def get_rate(session: AsyncSession, items: str):
    items: dict = json.loads(items)
    rate = await tools.get_value(
        session=session, value_name="RATE_RUB_USD", cache_=False
    )
    if items.get("item_2"):
        value = await session.scalar(
            select(Item.value).where(Item.code_name == "item_2")
        )
        rate = rate * (1 - (value / 100))
    return int(rate)


async def update_bank_storage(session: AsyncSession, amount: int):
    await session.execute(
        update(Value)
        .where(Value.name == "BANK_STORAGE")
        .values(value_int=Value.value_int + amount)
    )


async def exchange(session: AsyncSession, user: User, amount: int, rate: int, all: bool = True):
    BANK_PERCENT_FEE = await tools.get_value(
        session=session, value_name="BANK_PERCENT_FEE"
    )
    you_got, remains = divmod(amount, rate)
    you_change = you_got * rate
    bank_fee = int(you_got * (BANK_PERCENT_FEE / 100))
    bank_fee = bank_fee if bank_fee > 0 else 1 if you_got > 1 else 0
    if bank_fee:
        await update_bank_storage(session, bank_fee)
    you_got = you_got - bank_fee
    if all:
        user.rub = remains
    else:
        user.rub -= amount - remains
    return you_change, bank_fee if bank_fee > 0 else None, you_got
