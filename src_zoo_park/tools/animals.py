from sqlalchemy import select
from db import Text, Button, Value, Animal, Unity, User
from init_db import _sessionmaker_for_func
import json
from collections import defaultdict


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


async def get_price_animal(animal_code_name: str, unity_idpk: int | None) -> int:
    async with _sessionmaker_for_func() as session:
        discount = (
            await get_unity_data_for_price_animal(unity_idpk) if unity_idpk else 0
        )
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


async def get_top_unity_by_animal() -> tuple[int, dict]:
    table_for_compare = {}
    async with _sessionmaker_for_func() as session:
        unitys = await session.scalars(select(Unity))
        unitys = unitys.all()
        for unity in unitys:
            member_ids = unity.get_members_idpk()
            animals = defaultdict(int)
            for idpk in member_ids:
                user = await session.get(User, int(idpk))
                animals_user = user.get_dict_animals()
                for animal_name, num_animal in animals_user.items():
                    animals[animal_name] += num_animal
            max_animal = max(animals, key=animals.get)
            table_for_compare[unity.idpk] = {max_animal: animals[max_animal]}
        top_unity = max(
            table_for_compare, key=lambda x: next(iter(table_for_compare[x].values()))
        )
        return int(top_unity), table_for_compare[top_unity]


async def get_income_animal(animal: Animal, unity_idpk: int):
    async with _sessionmaker_for_func() as session:
        if unity_idpk:
            unity_idpk_top, animal_top = await get_top_unity_by_animal()
            if (
                unity_idpk_top == unity_idpk
                and animal.code_name == list(animal_top.keys())[0]
            ):
                bonus = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "BONUS_FOR_AMOUNT_ANIMALS"
                    )
                )
                animal_income = animal.income * (1 + (bonus / 100))
                return int(animal_income)
        return animal.income
