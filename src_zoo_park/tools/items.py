from sqlalchemy import select
from db import Item, User
import json
import tools
from sqlalchemy.ext.asyncio import AsyncSession
import math


async def get_all_name_items(session: AsyncSession):
    name_items = await session.execute(select(Item.name, Item.code_name))
    return name_items.all()


async def get_items_data_to_kb(
    session: AsyncSession, items: str
) -> list[tuple[str, str, str]]:
    decoded_dict: dict = json.loads(items)
    data = []
    EMOJI_FOR_ACTIVATE_ITEM = await tools.get_value(
        session=session, value_name="EMOJI_FOR_ACTIVATE_ITEM", value_type="str"
    )
    for key, value in decoded_dict.items():
        name_item = await session.scalar(select(Item.name).where(Item.code_name == key))
        value = EMOJI_FOR_ACTIVATE_ITEM if value == True else ""
        data.append((name_item, key, value))
    return data


async def get_row_items_for_kb(session: AsyncSession):
    row_items = await tools.get_value(session=session, value_name="ROW_ITEMS_FOR_KB")
    return row_items


async def get_size_items_for_kb(session: AsyncSession):
    size_items = await tools.get_value(session=session, value_name="SIZE_ITEMS_FOR_KB")
    return size_items


async def count_page_items(session: AsyncSession, items: str) -> int:
    decoded_dict: dict = json.loads(items)
    size_items = await get_size_items_for_kb()
    return math.ceil(len(decoded_dict) / size_items)


async def get_status_item(items: str, code_name_item: str):
    decoded_dict: dict = json.loads(items)
    return decoded_dict[code_name_item]


async def add_item(
    session: AsyncSession,
    self: User,
    code_name_item: str,
    is_activate: bool = False,
) -> None:
    decoded_dict: dict = json.loads(self.items)
    decoded_dict[code_name_item] = is_activate
    self.items = json.dumps(decoded_dict, ensure_ascii=False)


async def activate_item(
    session: AsyncSession, self: User, code_name_item: str, is_active: bool = True
) -> None:
    decoded_dict: dict = json.loads(self.items)
    decoded_dict[code_name_item] = is_active
    self.items = json.dumps(decoded_dict, ensure_ascii=False)
    # await session.commit()


async def deactivate_all_items(session: AsyncSession, self: User) -> None:
    decoded_dict: dict = json.loads(self.items)
    for key in decoded_dict:
        decoded_dict[key] = False
    self.items = json.dumps(decoded_dict, ensure_ascii=False)
    # await session.commit()
