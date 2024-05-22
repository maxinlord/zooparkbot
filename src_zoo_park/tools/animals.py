from sqlalchemy import select
from db import Text, Button, Value, Animal
from init_db import _sessionmaker_for_func
import json


async def add_animal(animals: str, code_name_animal: str, quantity: int) -> str:
    decoded_dict: dict = json.loads(animals)
    if code_name_animal in decoded_dict:
        decoded_dict[code_name_animal] += quantity
    else:
        decoded_dict[code_name_animal] = quantity
    return json.dumps(decoded_dict, ensure_ascii=False)


async def get_all_animals() -> list[Animal]:
    async with _sessionmaker_for_func() as session:
        r = await session.scalars(
            select(Animal).where(Animal.code_name.contains("-"))
        )
        return r.all()


async def get_all_quantity_animals() -> list[int]:
    async with _sessionmaker_for_func() as session:
        quantitys = await session.scalar(
            select(Value.value_str).where(Value.name == "QUANTITYS_FOR_RANDOM_MERCHANT")
        )
        quantitys = map(lambda x: int(x.strip()), quantitys.split(","))
        return list(quantitys)
