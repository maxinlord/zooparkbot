from sqlalchemy import select
from db import Text, Button, Value, Animal, Unity
from init_db import _sessionmaker_for_func
import json


async def get_all_animals() -> list[Animal]:
    async with _sessionmaker_for_func() as session:
        r = await session.scalars(select(Animal).where(Animal.code_name.contains("-")))
        return r.all()


async def get_quantity_animals_for_rmerchant() -> list[int]:
    async with _sessionmaker_for_func() as session:
        quantitys = await session.scalar(
            select(Value.value_str).where(Value.name == "QUANTITYS_FOR_RANDOM_MERCHANT")
        )
        quantitys = map(lambda x: int(x.strip()), quantitys.split(","))
        return list(quantitys)


async def get_quantity_animals_for_rshop() -> list[int]:
    async with _sessionmaker_for_func() as session:
        quantitys = await session.scalar(
            select(Value.value_str).where(Value.name == "QUANTITYS_FOR_RARITY_SHOP")
        )
        quantitys = map(lambda x: int(x.strip()), quantitys.split(","))
        return list(quantitys)


async def get_price_animal(animal_code_name: str, unity_idpk: int) -> int:
    async with _sessionmaker_for_func() as session:
        discount = await get_unity_data_for_price_animal(unity_idpk)
        price = await session.scalar(
            select(Animal.price).where(Animal.code_name == animal_code_name)
        )
        if discount:
            price *= 1 - (discount / 100)
        return int(price)


async def get_unity_data_for_price_animal(idpk_unity: int):
    async with _sessionmaker_for_func() as session:
        unity = await session.get(Unity, idpk_unity)
        bonus = 0
        if unity.level == 2:
            bonus = await session.scalar(
                select(Value.value_int).where(
                    Value.name == "BONUS_DISCOUNT_FOR_ANIMAL_2ND_LVL"
                )
            )
        elif unity.level == 3:
            bonus = await session.scalar(
                select(Value.value_int).where(
                    Value.name == "BONUS_DISCOUNT_FOR_ANIMAL_3RD_LVL"
                )
            )
    return bonus
