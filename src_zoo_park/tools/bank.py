import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Value, Aviary, Item
from sqlalchemy import select, update
import random
import tools
import json
from datetime import datetime


async def get_rate(session: AsyncSession, user: User):
    rate = await tools.get_value(
        session=session, value_name="RATE_RUB_USD", cache_=False
    )
    if await tools.get_status_item(items=user.items, code_name_item="item_2"):
        value = await session.scalar(
            select(Item.value).where(Item.code_name == "item_2")
        )
        rate = rate * (1 - (value / 100))
    if d := await tools.get_values_from_item(items=user.items, code_name_item="item_6"):
        time_str = d.get("date_end")
        if not time_str:
            pass
        elif datetime.fromisoformat(time_str) >= datetime.now():
            rate = await tools.get_value(session=session, value_name="MIN_RATE_RUB_USD")
    return int(rate)


async def update_bank_storage(session: AsyncSession, amount: int):
    await session.execute(
        update(Value)
        .where(Value.name == "BANK_STORAGE")
        .values(value_int=Value.value_int + amount)
    )


async def exchange(
    session: AsyncSession, user: User, amount: int, rate: int, all: bool = True
):
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


async def get_weight_rate_bank(session: AsyncSession) -> list[float]:
    weight_rate = await tools.get_value(
        session=session, value_name="WEIGHT_RATE_BANK", value_type="str"
    )
    return [float(i.strip()) for i in weight_rate.split(",")]


async def get_increase_rate_bank(
    session: AsyncSession,
) -> tuple[list[int], list[int]]:
    increase_rate_plus, increase_rate_minus = await asyncio.gather(
        tools.get_value(
            session=session, value_name="INCREASE_PLUS_RATE_BANK", value_type="str"
        ),
        tools.get_value(
            session=session, value_name="INCREASE_MINUS_RATE_BANK", value_type="str"
        ),
    )
    increase_rate_plus = [int(i.strip()) for i in increase_rate_plus.split(", ")]
    increase_rate_minus = [int(i.strip()) for i in increase_rate_minus.split(", ")]
    return increase_rate_plus, increase_rate_minus
