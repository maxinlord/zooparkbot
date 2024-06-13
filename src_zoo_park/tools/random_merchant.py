from sqlalchemy import select
from db import RandomMerchant, Animal, User
from faker import Faker
import random
import tools
from sqlalchemy.ext.asyncio import AsyncSession

# Создание экземпляра Faker для русского языка
fake = Faker("ru_RU")


async def create_random_merchant(session: AsyncSession, user: User) -> RandomMerchant:
    """Создание случайного торговца"""
    MAX_DISCOUNT = await tools.get_value(session=session, value_name="MAX_DISCOUNT")
    random_animal = await tools.get_random_animal(
        session=session, user_animals=user.animals
    )
    random_quantity_animals = await tools.gen_quantity_animals(session=session)
    random_discount = random.randint(-MAX_DISCOUNT, MAX_DISCOUNT)
    price_with_discount = calculate_price_with_discount(
        price=random_animal.price * random_quantity_animals,
        discount=random_discount,
    )
    random_price = await gen_price(session=session, user=user)
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


async def gen_price(session: AsyncSession, user: User) -> int:
    MIN_RANDOM_PRICE = await tools.get_value(
        session=session, value_name="MIN_RANDOM_PRICE"
    )
    i = await tools.income_(session=session, user=user)
    MAX_RANDOM_PRICE = MIN_RANDOM_PRICE * 3 if i == 0 else i * 12 * 60 // 67
    price = random.randint(MIN_RANDOM_PRICE, MAX_RANDOM_PRICE)
    return price
