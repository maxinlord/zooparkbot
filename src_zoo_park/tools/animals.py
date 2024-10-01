import random
from sqlalchemy import select
from db import Animal, Unity, User

import json
import tools
import game_variables

from sqlalchemy.ext.asyncio import AsyncSession


async def get_all_animals(session: AsyncSession) -> list[Animal]:
    result = await session.scalars(select(Animal).where(Animal.code_name.contains("-")))
    return result.all()


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


async def get_income_animal(
    session: AsyncSession,
    animal: Animal,
    unity_idpk: int,
    info_about_items: str,
):
    animal_income = animal.income
    name_prop = f'{animal.code_name}:animal_income'
    if v:=tools.get_value_prop_from_iai(info_about_items=info_about_items, name_prop=name_prop):
        animal_income = animal_income * (1 + v / 100)
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


# async def _get_income_animal(
#     session: AsyncSession,
#     animal: Animal,
#     unity_idpk: int,
# ):
#     animal_income = animal.income
#     if unity_idpk:
#         unity_idpk_top, animal_top = await tools.get_top_unity_by_animal(
#             session=session
#         )
#         if (
#             unity_idpk_top == unity_idpk
#             and animal.code_name == list(animal_top.keys())[0]
#         ):
#             bonus = await tools.get_value(
#                 session=session, value_name="BONUS_FOR_AMOUNT_ANIMALS"
#             )
#             animal_income = animal_income * (1 + (bonus / 100))
#     return int(animal_income)


async def get_random_animal(session: AsyncSession, user_animals: str) -> Animal:
    dict_animals: dict = json.loads(user_animals)
    if not dict_animals:
        animal_names_to_choice = await tools.fetch_and_parse_str_value(
            session=session,
            value_name="START_ANIMALS_FOR_RMERCHANT",
            func_to_element=str,
        )
    else:
        animal_names_to_choice = [
            animal_name.split("_")[0] for animal_name in dict_animals
        ]
    animal_name = random.choice(animal_names_to_choice)
    rarity = random.choices(
        population=game_variables.rarities,
        weights=await tools.fetch_and_parse_str_value(
            session=session,
            value_name="WEIGHTS_FOR_RANDOM_MERCHANT",
            func_to_element=float,
        ),
    )
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == animal_name + rarity[0])
    )
    return animal


async def get_animal_with_random_rarity(session: AsyncSession, animal: str) -> Animal:
    rarity = random.choices(
        population=game_variables.rarities,
        weights=await tools.fetch_and_parse_str_value(
            session=session,
            value_name="WEIGHTS_FOR_RANDOM_MERCHANT",
            func_to_element=float,
        ),
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


async def get_average_price_animals(session: AsyncSession, animals_code_name: set[str]):
    result = await session.execute(
        select(Animal.price).where(Animal.code_name.in_(animals_code_name))
    )
    prices = [row[0] for row in result]
    return sum(prices) / len(prices)


async def magic_count_animal_for_kb(remain_seats, balance, price_per_one_animal):
    count_enough_animal = balance // price_per_one_animal
    count_enough_animal = min(count_enough_animal, remain_seats)
    return count_enough_animal