from sqlalchemy import select
from db import User, Value, Aviary, Item
import random
import tools

from sqlalchemy.ext.asyncio import AsyncSession


async def referral_bonus(session: AsyncSession, referral: User):
    bonus = await tools.get_value(session=session, value_name="REFERRAL_BONUS")
    referral.usd += bonus
    await session.commit()
    return bonus


async def referrer_bonus(session: AsyncSession, referrer: User):
    bonus = await tools.get_value(session=session, value_name="REFERRER_BONUS")
    referrer.usd += bonus
    await session.commit()
    return bonus


async def bonus_for_sub_on_chat(session: AsyncSession, user: User):
    bonus = await tools.get_value(
        session=session, value_name="SUBSCRIPTION_BONUS_ON_CHAT"
    )
    user.usd += bonus
    await session.commit()
    return bonus


async def bonus_for_sub_on_channel(session: AsyncSession, user: User):
    bonus = await tools.get_value(
        session=session, value_name="SUBSCRIPTION_BONUS_ON_CHANNEL"
    )
    user.usd += bonus
    return bonus


async def fetch_and_parse(session: AsyncSession, name: str, parse_func):
    value_str = await session.scalar(select(Value.value_str).where(Value.name == name))
    return [parse_func(v.strip()) for v in value_str.split(",")]


async def handle_rub_bonus(user, session):
    income = await tools.income_(session=session, user=user)
    if income == 0:
        income = 12
    income_for_8_hour = income * 480
    rub_to_add = random.randint(income_for_8_hour // 3, income_for_8_hour)
    user.rub += rub_to_add
    return {"rub_to_add": rub_to_add}


async def handle_usd_bonus(user, session):
    weights = await fetch_and_parse(session, "WEIGHTS_FOR_BONUS_USD", float)
    types_usd_bonus = await fetch_and_parse(session, "TYPES_USD_BONUS", int)
    usd_to_add = random.choices(population=types_usd_bonus, weights=weights)[0]
    user.usd += usd_to_add
    return {"usd_to_add": usd_to_add}


async def handle_aviary_bonus(user, session):
    types_aviaries = list(await session.scalars(select(Aviary.code_name)))
    aviary_to_add = random.choice(types_aviaries)
    amount_to_add = random.randint(1, 5)
    await tools.add_aviary(
        session=session,
        self=user,
        code_name_aviary=aviary_to_add,
        quantity=amount_to_add,
        is_buy=False,
    )
    return {"aviary_to_add": aviary_to_add, "amount_to_add": amount_to_add}


async def handle_animal_bonus(user: User, session):
    animal = await tools.get_random_animal(session=session, user_animals=user.animals)
    amount_to_add = random.randint(
        1,
        await tools.get_remain_seats(
            session=session,
            aviaries=user.aviaries,
            amount_animals=await tools.get_total_number_animals(self=user),
        ),
    )
    await tools.add_animal(
        self=user,
        code_name_animal=animal.code_name,
        quantity=amount_to_add,
    )
    return {"animal_to_add": animal.name, "amount_to_add": amount_to_add}


async def handle_item_bonus(user: User, session):
    items = list(await session.scalars(select(Item)))
    item_to_add: Item = random.choice(items)
    if item_to_add.code_name in user.items:
        amount = item_to_add.price // 2
        dict_currencies = {
            "paw_coins": user.paw_coins,
            "rub": user.rub,
            "usd": user.usd,
        }
        dict_currencies[item_to_add.currency] += amount
        return {f"{item_to_add.currency}_to_add": amount}
    await tools.add_item(self=user, code_name_item=item_to_add.code_name)
    return {"item_to_add": item_to_add.name}


async def bonus_(session: AsyncSession, user: User):
    types_bonus = ["rub", "usd", "aviary", "animal", "item"]
    weights = await fetch_and_parse(session, "WEIGHTS_FOR_BONUS", float)
    bonus_type = random.choices(population=types_bonus, weights=weights)[0]
    handlers = {
        "rub": handle_rub_bonus,
        "usd": handle_usd_bonus,
        "aviary": handle_aviary_bonus,
        "animal": handle_animal_bonus,
        "item": handle_item_bonus,
    }
    data_about_bonus = {bonus_type: await handlers[bonus_type](user, session)}
    return data_about_bonus
