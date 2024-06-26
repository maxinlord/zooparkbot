from sqlalchemy import select
from db import Value
from cache import value_cache
from sqlalchemy.ext.asyncio import AsyncSession


async def get_value(session: AsyncSession, value_name: str, value_type: str = "int", cache_: bool = True):
    if value_name in value_cache and cache_:
        return value_cache[value_name]
    if value_type == "int":
        value = await session.scalar(
            select(Value.value_int).where(Value.name == value_name)
        )
    elif value_type == "str":
        value = await session.scalar(
            select(Value.value_str).where(Value.name == value_name)
        )
    return value
