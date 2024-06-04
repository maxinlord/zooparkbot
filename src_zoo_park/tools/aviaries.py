from sqlalchemy import select, and_
from db import Text, Button, Value, Item, Aviary
from init_db import _sessionmaker_for_func
import json


async def get_all_name_aviaries():
    async with _sessionmaker_for_func() as session:
        name_items = await session.execute(select(Aviary.name, Aviary.code_name))
    return name_items.all()


async def get_quantity_animals_for_avi() -> list[int]:
    async with _sessionmaker_for_func() as session:
        quantities = await session.scalar(
            select(Value.value_str).where(Value.name == "QUANTITYS_FOR_AVIARIES")
        )
        quantities = map(lambda x: int(x.strip()), quantities.split(","))
        return list(quantities)


async def get_total_number_seats(aviaries: str) -> int:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(aviaries)
        all_seats = 0
        for key, value in decoded_dict.items():
            all_seats += (
                await session.scalar(select(Aviary.size).where(Aviary.code_name == key))
                * value
            )
        return all_seats


async def get_remain_seats(aviaries: str, amount_animals: int) -> int:
    all_seats = await get_total_number_seats(aviaries)
    return all_seats - amount_animals