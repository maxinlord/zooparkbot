import json

from db import Aviary, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import tools


async def get_name_and_code_name(session: AsyncSession):
    aviaries = await session.scalars(select(Aviary))
    return [(aviary.name_with_size, aviary.code_name) for aviary in aviaries]


async def get_total_number_seats(session: AsyncSession, aviaries: str) -> int:
    decoded_dict: dict = json.loads(aviaries)
    all_seats = 0
    for key, value in decoded_dict.items():
        all_seats += (
            await session.scalar(select(Aviary.size).where(Aviary.code_name == key))
            * value["quantity"]
        )
    return all_seats


async def get_remain_seats(session: AsyncSession, user: User) -> int:
    all_seats = await get_total_number_seats(session=session, aviaries=user.aviaries)
    amount_animals = await tools.get_total_number_animals(self=user)
    return all_seats - amount_animals


async def add_aviary(
    session: AsyncSession,
    self: User,
    code_name_aviary: str,
    quantity: int,
    is_buy: bool = True,
) -> None:
    decoded_dict: dict = json.loads(self.aviaries)
    INCREASE_FOR_AVIARY = await tools.get_value(
        session, value_name="INCREASE_FOR_AVIARY"
    )

    if code_name_aviary in decoded_dict and is_buy:
        decoded_dict[code_name_aviary]["price"] += int(
            decoded_dict[code_name_aviary]["price"] * INCREASE_FOR_AVIARY / 100
        )
        decoded_dict[code_name_aviary]["buy_count"] += 1
        decoded_dict[code_name_aviary]["quantity"] += quantity
    elif code_name_aviary in decoded_dict:
        decoded_dict[code_name_aviary]["quantity"] += quantity
    else:
        price_aviary = await session.scalar(
            select(Aviary.price).where(Aviary.code_name == code_name_aviary)
        )
        decoded_dict[code_name_aviary] = {
            "quantity": quantity,
            "buy_count": 1,
            "price": price_aviary,
        }
    self.aviaries = json.dumps(decoded_dict, ensure_ascii=False)
    # await session.commit()


async def get_price_aviaries(
    session: AsyncSession, aviaries: str, code_name_aviary: str, info_about_items: str
) -> int:
    aviaries: dict = json.loads(aviaries)
    aviary_price = 0
    if aviaries.get(code_name_aviary):
        aviary_price = aviaries[code_name_aviary]["price"]
    else:
        aviary_price = await session.scalar(
            select(Aviary.price).where(Aviary.code_name == code_name_aviary)
        )
    if v := tools.get_value_prop_from_iai(
        info_about_items=info_about_items, name_prop="aviaries_sale"
    ):
        aviary_price = aviary_price * (1 - v / 100)
    return int(aviary_price)
