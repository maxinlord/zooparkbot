from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Value, Aviary, Item
from sqlalchemy import select
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
