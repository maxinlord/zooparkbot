from sqlalchemy import select
from init_db import _sessionmaker_for_func
from db import RandomMerchant, Animal, Value
from faker import Faker
import random
from config import rarities
from tools import get_value
from sqlalchemy.ext.asyncio import AsyncSession
import json

# Создание экземпляра Faker для русского языка
fake = Faker("ru_RU")


async def create_random_merchant(session: AsyncSession, id_user: int) -> RandomMerchant:
    """Создание случайного мерчанта"""
    r = await session.scalars(select(Animal).where(Animal.code_name.contains("_")))
    MAX_DISCOUNT = await get_value(session=session, value_name="MAX_DISCOUNT")
    random_animal = random.choice(r.all())
    random_quantity_animals = await gen_quantity_animals(session=session)
    random_discount = random.randint(-MAX_DISCOUNT, MAX_DISCOUNT)
    price_with_discount = calculate_price_with_discount(
        price=random_animal.price * random_quantity_animals,
        discount=random_discount,
    )
    random_price = await gen_price(session=session)
    rm = RandomMerchant(
        id_user=id_user,
        name=fake.first_name_male(),
        code_name_animal=random_animal.code_name,
        discount=random_discount,
        price_with_discount=price_with_discount,
        quantity_animals=random_quantity_animals,
        price=random_price,
    )
    session.add(rm)
    await session.commit()
    return rm


def calculate_price_with_discount(price: int, discount: int) -> int:
    if discount > 0:
        price *= 1 + discount / 100
    elif discount < 0:
        price *= 1 - abs(discount) / 100
    return round(price)


async def gen_quantity_animals(session: AsyncSession) -> int:
    MAX_QUANTITY_ANIMALS = await get_value(
        session=session, value_name="MAX_QUANTITY_ANIMALS"
    )
    quantity_animals = random.randint(1, MAX_QUANTITY_ANIMALS)
    return quantity_animals


async def gen_price(session: AsyncSession) -> int:
    MAX_RANDOM_PRICE = await get_value(
        session=session, value_name="MAX_RANDOM_PRICE"
    )
    MIN_RANDOM_PRICE = await get_value(
        session=session, value_name="MIN_RANDOM_PRICE"
    )
    price = random.randint(MIN_RANDOM_PRICE, MAX_RANDOM_PRICE)
    return price


async def get_weights(session: AsyncSession) -> list:
    w_str = await get_value(session=session, value_name="WEIGHTS_FOR_RANDOM_MERCHANT", value_type='str')
    weights = [float(w.strip()) for w in w_str.split(",")]
    return weights


async def get_animal_with_random_rarity(session: AsyncSession, animal: str) -> Animal:
    rarity = random.choices(
        population=rarities,
        weights=await get_weights(session=session),
    )
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == animal + rarity[0])
    )
    return animal


async def get_random_animal(session: AsyncSession, user_animals: str) -> Animal:
    dict_animals: dict = json.loads(user_animals)
    if not dict_animals:
        r = await get_value(session=session, value_name="START_ANIMALS_FOR_RMERCHANT", value_type='str')
        c_names = [c_name.strip() for c_name in r.split(",")]
    else:
        c_names = [c_name.split("_")[0] for c_name in dict_animals]
    animal_name = random.choice(c_names)
    rarity = random.choices(
        population=rarities,
        weights=await get_weights(session=session),
    )
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == animal_name + rarity[0])
    )
    return animal
