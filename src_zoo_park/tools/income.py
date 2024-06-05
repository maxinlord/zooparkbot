from sqlalchemy import select, and_
from db import Text, Button, Value, Item, Aviary, User, Animal, Unity
from init_db import _sessionmaker_for_func
import json
from tools import get_top_unity_by_animal


async def income(user: User):
    unity_idpk = int(user.current_unity.split(":")[-1]) if user.current_unity else None
    animals: dict = json.loads(user.animals)
    income = await income_from_animal(animals, unity_idpk)
    if unity_idpk:
        unity_data = await get_unity_data_for_income(unity_idpk)
        if unity_data["lvl"] in [1, 2, 3]:
            income *= 1 + (unity_data["bonus"] / 100)
    return int(income)


async def _get_income_animal(animal: Animal, unity_idpk: int | None, bonus: int):
    async with _sessionmaker_for_func() as session:
        if unity_idpk:
            unity_idpk_top, animal_top = await get_top_unity_by_animal()
            if (
                unity_idpk_top == unity_idpk
                and animal.code_name == list(animal_top.keys())[0]
            ):
                animal_income = animal.income * (1 + (bonus / 100))
                return int(animal_income)
        return animal.income


async def income_from_animal(animals: dict, unity_idpk: int):
    income = 0
    async with _sessionmaker_for_func() as session:
        bonus = await session.scalar(
            select(Value.value_int).where(Value.name == "BONUS_FOR_AMOUNT_ANIMALS")
        )
        for animal, quantity in animals.items():
            animal = await session.scalar(
                select(Animal).where(Animal.code_name == animal)
            )
            animal_income = await _get_income_animal(
                animal=animal, unity_idpk=unity_idpk, bonus=bonus
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
