from sqlalchemy import select, and_
from db import Text, Button, Value, Item, Aviary
from init_db import _sessionmaker_for_func
import json
from tools import get_value

from sqlalchemy.ext.asyncio import AsyncSession


async def get_all_name_and_size_aviaries():
    async with _sessionmaker_for_func() as session:
        name_items = await session.execute(select(Aviary.name, Aviary.code_name, Aviary.size))
    return name_items.all()


async def get_quantity_animals_for_avi() -> list[int]:
    async with _sessionmaker_for_func() as session:
        quantities = await get_value(session, value_name="QUANTITYS_FOR_AVIARIES", value_type='str')
        quantities = map(lambda x: int(x.strip()), quantities.split(","))
        return list(quantities)


async def get_total_number_seats(session: AsyncSession, aviaries: str) -> int:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(aviaries)
        all_seats = 0
        for key, value in decoded_dict.items():
            all_seats += (
                await session.scalar(select(Aviary.size).where(Aviary.code_name == key))
                * value
            )
        return all_seats


async def get_remain_seats(session: AsyncSession, aviaries: str, amount_animals: int) -> int:
    all_seats = await get_total_number_seats(session=session, aviaries=aviaries)
    return all_seats - amount_animals