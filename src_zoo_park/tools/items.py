from sqlalchemy import select, and_
from db import Text, Button, Value, Item
from init_db import _sessionmaker_for_func
import json


async def get_all_name_items():
    async with _sessionmaker_for_func() as session:
        name_items = await session.execute(select(Item.name, Item.code_name))
    return name_items.all()


async def get_items_data_to_kb(items: str) -> list[tuple[str, str, str]]:
    decoded_dict: dict = json.loads(items)
    data = []
    async with _sessionmaker_for_func() as session:
        EMOJI_FOR_ACTIVATE_ITEM = await session.scalar(
            select(Value.value_str).where(Value.name == "EMOJI_FOR_ACTIVATE_ITEM")
        )
        for key, value in decoded_dict.items():
            name_item = await session.scalar(
                select(Item.name).where(Item.code_name == key)
            )
            value = EMOJI_FOR_ACTIVATE_ITEM if value == True else ""
            data.append((name_item, key, value))
    return data


async def get_row_items_for_kb():
    async with _sessionmaker_for_func() as session:
        row_items = await session.scalar(
            select(Value.value_int).where(Value.name == "ROW_ITEMS_FOR_KB")
        )
    return row_items


async def get_size_items_for_kb():
    async with _sessionmaker_for_func() as session:
        size_items = await session.scalar(
            select(Value.value_int).where(Value.name == "SIZE_ITEMS_FOR_KB")
        )
    return size_items


async def count_page_items(items: str) -> int:
    decoded_dict: dict = json.loads(items)
    size_items = await get_size_items_for_kb()
    async with _sessionmaker_for_func() as session:
        len_items = len(decoded_dict)
        remains = len_items % size_items
        return (len_items // size_items) + 1 if remains else len_items // size_items


async def get_status_item(items: str, code_name_item: str):
    decoded_dict: dict = json.loads(items)
    return decoded_dict[code_name_item]
