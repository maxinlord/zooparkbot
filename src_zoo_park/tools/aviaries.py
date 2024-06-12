from sqlalchemy import select
from db import Aviary, User
import json
import tools

from sqlalchemy.ext.asyncio import AsyncSession
import tools


async def get_all_name_and_size_aviaries(session: AsyncSession):
    name_items = await session.execute(
        select(Aviary.name, Aviary.code_name, Aviary.size)
    )
    return name_items.all()


async def get_quantity_animals_for_avi(session: AsyncSession) -> list[int]:
    quantities = await tools.get_value(
        session, value_name="QUANTITIES_FOR_AVIARIES", value_type="str"
    )
    quantities = map(lambda x: int(x.strip()), quantities.split(","))
    return list(quantities)


async def get_total_number_seats(session: AsyncSession, aviaries: str) -> int:
    decoded_dict: dict = json.loads(aviaries)
    all_seats = 0
    for key, value in decoded_dict.items():
        all_seats += (
            await session.scalar(select(Aviary.size).where(Aviary.code_name == key))
            * value["quantity"]
        )
    return all_seats


async def get_remain_seats(
    session: AsyncSession, aviaries: str, amount_animals: int
) -> int:
    all_seats = await get_total_number_seats(session=session, aviaries=aviaries)
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
    session: AsyncSession, aviaries: str, code_name_aviary: str
) -> int:
    decoded_dict: dict = json.loads(aviaries)
    if aviaries and decoded_dict.get(code_name_aviary):
        return decoded_dict[code_name_aviary]["price"]
    else:
        return await session.scalar(
            select(Aviary.price).where(Aviary.code_name == code_name_aviary)
        )
