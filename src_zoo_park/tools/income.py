from sqlalchemy import select, and_
from db import Text, Button, Value, Item, Aviary, User, Animal, Unity
from init_db import _sessionmaker_for_func
import json


async def income(user: User):
    animals: dict = json.loads(user.animals)
    income = await income_from_animal(animals)
    if user.current_unity:
        unity_idpk = int(user.current_unity.split(":")[-1])
        unity_data = await get_unity_data_for_income(unity_idpk)
        if unity_data["lvl"] in [1, 2, 3]:
            income *= 1 + (unity_data["bonus"] / 100)
    return int(income)


async def income_from_animal(animals: dict):
    income = 0
    async with _sessionmaker_for_func() as session:
        for animal, quantity in animals.items():
            animal_income = await session.scalar(
                select(Animal.income).where(Animal.code_name == animal)
            )
            income += animal_income * quantity
    return income



async def get_unity_data_for_income(idpk_unity: int):
    data = {}
    async with _sessionmaker_for_func() as session:
        unity = await session.get(Unity, idpk_unity)
        data["lvl"] = unity.level
        if unity.level in [1, 2]:
            data["bonus"] = await session.scalar(
                select(Value.value_int).where(
                    Value.name == "BONUS_ADD_TO_INCOME_1ST_LVL"
                )
            )
        elif unity.level == 3:
            data["bonus"] = await session.scalar(
                select(Value.value_int).where(
                    Value.name == "BONUS_ADD_TO_INCOME_3RD_LVL"
                )
            )
    return data