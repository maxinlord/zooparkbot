import asyncio
from sqlalchemy import select
from db import RandomMerchant, Animal, User
from faker import Faker
import random
import tools
from sqlalchemy.ext.asyncio import AsyncSession
import json

# Создание экземпляра Faker для русского языка
fake = Faker("ru_RU")


async def create_random_merchant(session: AsyncSession, user: User) -> RandomMerchant:
    """Создание случайного торговца"""
    MAX_DISCOUNT = await tools.get_value(session=session, value_name="MAX_DISCOUNT")
    random_animal = await tools.get_random_animal(
        session=session, user_animals=user.animals
    )
    random_quantity_animals = await tools.gen_quantity_animals(
        session=session, user=user
    )
    random_discount = random.randint(-MAX_DISCOUNT, MAX_DISCOUNT)
    price_with_discount = calculate_price_with_discount(
        price=random_animal.price * random_quantity_animals,
        discount=random_discount,
    )
    random_price = await gen_price(session=session, animals=user.animals)
    rm = RandomMerchant(
        id_user=user.id_user,
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


async def get_weights_rmerchant(session: AsyncSession) -> list:
    w_str = await tools.get_value(
        session=session, value_name="WEIGHTS_FOR_RANDOM_MERCHANT", value_type="str"
    )
    weights = [float(w.strip()) for w in w_str.split(",")]
    return weights


async def gen_price(session: AsyncSession, animals: str) -> int:
    animals_dict = json.loads(animals)
    MAX_QUANTITY_ANIMALS, price = await asyncio.gather(
        tools.get_value(session=session, value_name="MAX_QUANTITY_ANIMALS"),
        (
            tools.get_average_price_animals(
                session=session, animals_code_name=set(animals_dict.keys())
            )
            if animals_dict
            else session.scalar(
                select(Animal.price).where(Animal.code_name == "animal1_rare")
            )
        ),
    )

    if animals_dict:
        price = price * (MAX_QUANTITY_ANIMALS - 2)
    else:
        price = price * MAX_QUANTITY_ANIMALS

    return int(price)
