import random
from sqlalchemy import select
from db import Animal, Unity, User, Item

import json
import tools
import config

from sqlalchemy.ext.asyncio import AsyncSession


async def get_all_animals(session: AsyncSession) -> list[Animal]:
    result = await session.scalars(select(Animal).where(Animal.code_name.contains("-")))
    return result.all()


async def get_quantity_animals_for_rmerchant(session: AsyncSession) -> list[int]:
    quantities = await tools.get_value(
        session=session, value_name="QUANTITIES_FOR_RANDOM_MERCHANT", value_type="str"
    )
    quantities = map(lambda x: int(x.strip()), quantities.split(","))
    return list(quantities)


async def get_quantity_animals_for_rshop(session: AsyncSession) -> list[int]:
    quantities = await tools.get_value(
        session=session, value_name="QUANTITIES_FOR_RARITY_SHOP", value_type="str"
    )
    quantities = map(lambda x: int(x.strip()), quantities.split(","))
    return list(quantities)


async def get_price_animal(
    session: AsyncSession, animal_code_name: str, unity_idpk: int | None
) -> int:
    discount = (
        await _get_unity_data_for_price_animal(session=session, idpk_unity=unity_idpk)
        if unity_idpk
        else 0
    )
    price = await session.scalar(
        select(Animal.price).where(Animal.code_name == animal_code_name)
    )
    if discount:
        price *= 1 - (discount / 100)
    return int(price)


async def _get_unity_data_for_price_animal(session: AsyncSession, idpk_unity: int):
    unity = await session.get(Unity, idpk_unity)
    bonus = 0
    if unity.level == 2:
        bonus = await tools.get_value(
            session=session, value_name="BONUS_DISCOUNT_FOR_ANIMAL_2ND_LVL"
        )
    elif unity.level == 3:
        bonus = await tools.get_value(
            session=session, value_name="BONUS_DISCOUNT_FOR_ANIMAL_3RD_LVL"
        )
    return bonus


async def _get_income_animal(
    session: AsyncSession,
    animal: Animal,
    unity_idpk: int,
):
    animal_income = animal.income
    if unity_idpk:
        unity_idpk_top, animal_top = await tools.get_top_unity_by_animal(
            session=session
        )
        if (
            unity_idpk_top == unity_idpk
            and animal.code_name == list(animal_top.keys())[0]
        ):
            bonus = await tools.get_value(
                session=session, value_name="BONUS_FOR_AMOUNT_ANIMALS"
            )
            animal_income = animal_income * (1 + (bonus / 100))
    return int(animal_income)


async def get_income_animal(
    session: AsyncSession,
    animal: Animal,
    unity_idpk: int,
    items: str,
):
    animal_income = animal.income
    if await tools.get_status_item(items=items, code_name_item="item_1"):
        item = await session.scalar(select(Item).where(Item.code_name == "item_1"))
        animal_income = animal_income * (1 + item.value / 100)
    if unity_idpk:
        unity_idpk_top, animal_top = await tools.get_top_unity_by_animal(
            session=session
        )
        if (
            unity_idpk_top == unity_idpk
            and animal.code_name == list(animal_top.keys())[0]
        ):
            bonus = await tools.get_value(
                session=session, value_name="BONUS_FOR_AMOUNT_ANIMALS"
            )
            animal_income = animal_income * (1 + (bonus / 100))
    return int(animal_income)


async def get_dict_animals(self: User) -> dict:
    decoded_dict: dict = json.loads(self.animals)
    return decoded_dict


def get_numbers_animals(self: User) -> list[int]:
    decoded_dict: dict = json.loads(self.animals)
    return list(decoded_dict.values())


async def add_animal(self: User, code_name_animal: str, quantity: int) -> None:
    decoded_dict: dict = json.loads(self.animals)
    if code_name_animal in decoded_dict:
        decoded_dict[code_name_animal] += quantity
    else:
        decoded_dict[code_name_animal] = quantity
    self.animals = json.dumps(decoded_dict, ensure_ascii=False)
    # await session.commit()


async def get_total_number_animals(self: User) -> int:
    decoded_dict: dict = json.loads(self.animals)
    return sum(decoded_dict.values())


async def get_random_animal(session: AsyncSession, user_animals: str) -> Animal:
    dict_animals: dict = json.loads(user_animals)
    if not dict_animals:
        r = await tools.get_value(
            session=session, value_name="START_ANIMALS_FOR_RMERCHANT", value_type="str"
        )
        c_names = [c_name.strip() for c_name in r.split(",")]
    else:
        c_names = [c_name.split("_")[0] for c_name in dict_animals]
    animal_name = random.choice(c_names)
    rarity = random.choices(
        population=config.rarities,
        weights=await tools.get_weights_rmerchant(session=session),
    )
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == animal_name + rarity[0])
    )
    return animal


async def get_animal_with_random_rarity(session: AsyncSession, animal: str) -> Animal:
    rarity = random.choices(
        population=config.rarities,
        weights=await tools.get_weights_rmerchant(session=session),
    )
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == animal + rarity[0])
    )
    return animal


async def gen_quantity_animals(session: AsyncSession, user: User) -> int:
    MAX_QUANTITY_ANIMALS = await tools.get_value(
        session=session, value_name="MAX_QUANTITY_ANIMALS"
    )
    num = await tools.get_total_number_animals(user)
    if num == 0:
        MAX_QUANTITY_ANIMALS = 2
    quantity_animals = random.randint(1, MAX_QUANTITY_ANIMALS)
    return quantity_animals


async def get_average_price_animals(
    session: AsyncSession, animals_code_name: set[str]
):
    result = await session.execute(
        select(Animal.price).where(Animal.code_name.in_(animals_code_name))
    )
    prices = [row[0] for row in result]
    return sum(prices) / len(prices)

