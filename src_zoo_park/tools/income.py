from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Animal, Unity, Item
import tools
import json


async def income_(session: AsyncSession, user: User):
    unity_idpk = int(user.current_unity.split(":")[-1]) if user.current_unity else None
    animals: dict = json.loads(user.animals)
    income = await income_from_animal(
        session=session, animals=animals, unity_idpk=unity_idpk
    )
    if await tools.get_status_item(items=user.items, code_name_item="item_1"):
        item = await session.scalar(select(Item).where(Item.code_name == "item_1"))
        income = income * (1 + item.value / 100)
    if unity_idpk:
        unity_data = await get_unity_data_for_income(
            session=session, idpk_unity=unity_idpk
        )
        if unity_data["lvl"] in [1, 2, 3]:
            income *= 1 + (unity_data["bonus"] / 100)
    return int(income)


async def income_from_animal(session: AsyncSession, animals: dict, unity_idpk: int):
    income = 0
    for animal, quantity in animals.items():
        animal = await session.scalar(select(Animal).where(Animal.code_name == animal))
        animal_income = await tools._get_income_animal(
            session=session,
            animal=animal,
            unity_idpk=unity_idpk,
        )
        income += animal_income * quantity
    return int(income)


async def get_unity_data_for_income(session: AsyncSession, idpk_unity: int):
    unity = await session.get(Unity, idpk_unity)
    data = {"lvl": unity.level}
    if unity.level in [1, 2]:
        data["bonus"] = await tools.get_value(
            session=session, value_name="BONUS_ADD_TO_INCOME_1ST_LVL"
        )
    elif unity.level == 3:
        data["bonus"] = await tools.get_value(
            session=session, value_name="BONUS_ADD_TO_INCOME_3RD_LVL"
        )
    return data
