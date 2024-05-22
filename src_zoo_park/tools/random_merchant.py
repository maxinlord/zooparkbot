import html
import re
from sqlalchemy import select
from init_db import _sessionmaker_for_func
from db import RandomMerchant, Animal, Value
from faker import Faker
import random
from math import ceil

# Создание экземпляра Faker для русского языка
fake = Faker("ru_RU")


async def create_random_merchant(id_user: int) -> RandomMerchant:
    """Создание случайного мерчанта"""
    async with _sessionmaker_for_func() as session:
        r = await session.scalars(select(Animal).where(Animal.code_name.contains('_')))
        MAX_DISCOUNT = await session.scalar(
            select(Value.value_int).where(Value.name == "MAX_DISCOUNT")
        )
        random_animal = random.choice(r.all())
        random_quantity_animals = await gen_quantity_animals()
        random_discount = random.randint(-MAX_DISCOUNT, MAX_DISCOUNT)
        price_with_discount = calculate_price_with_discount(
            price=random_animal.price * random_quantity_animals,
            discount=random_discount,
        )
        random_price = await gen_price()
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


async def gen_quantity_animals() -> int:
    async with _sessionmaker_for_func() as session:
        MAX_QUANTITY_ANIMALS = await session.scalar(
            select(Value.value_int).where(Value.name == "MAX_QUANTITY_ANIMALS")
        )
        quantity_animals = random.randint(1, MAX_QUANTITY_ANIMALS)
        return quantity_animals


async def gen_price() -> int:
    async with _sessionmaker_for_func() as session:
        MAX_RANDOM_PRICE = await session.scalar(
            select(Value.value_int).where(Value.name == "MAX_RANDOM_PRICE")
        )
        MIN_RANDOM_PRICE = await session.scalar(
            select(Value.value_int).where(Value.name == "MIN_RANDOM_PRICE")
        )
        price = random.randint(MIN_RANDOM_PRICE, MAX_RANDOM_PRICE)
        return price


async def get_weights() -> list:
    async with _sessionmaker_for_func() as session:
        w_str = await session.scalar(
            select(Value.value_str).where(Value.name == "WEIGHTS_FOR_RANDOM_MERCHANT")
        )
        weights = [float(w.strip()) for w in w_str.split(',')]
        return weights


async def get_animal_with_random_rarity(animal: str) -> Animal:
    async with _sessionmaker_for_func() as session:
        rarity = random.choices(
            population=["_rare", "_epic", "_mythical", "_legendary"],
            weights=await get_weights(),
        )
        animal = await session.scalar(
            select(Animal).where(Animal.code_name == animal + rarity[0])
        )
        return animal



async def get_random_animal() -> Animal:
    async with _sessionmaker_for_func() as session:
        c_names = await session.scalars(
            select(Animal.code_name).where(Animal.code_name.contains("-"))
        )
        c_names = [c_name.strip("-") for c_name in c_names]
        animal_name = random.choice(c_names)
        rarity = random.choices(
            population=["_rare", "_epic", "_mythical", "_legendary"],
            weights=await get_weights(),
        )
        animal = await session.scalar(
            select(Animal).where(Animal.code_name == animal_name + rarity[0])
        )
        return animal
