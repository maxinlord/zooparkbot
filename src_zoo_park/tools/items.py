from sqlalchemy import select
from db import Item, User
import json
import tools
from sqlalchemy.ext.asyncio import AsyncSession
import math


async def get_all_name_items(session: AsyncSession):
    items = await session.scalars(select(Item))
    return [(item.name_with_emoji, item.code_name) for item in items.all()]


async def get_items_data_to_kb(
    session: AsyncSession, items: str
) -> list[tuple[str, str, str]]:
    decoded_dict: dict = json.loads(items)
    data = []
    EMOJI_FOR_ACTIVATE_ITEM = await tools.get_value(
        session=session,
        value_name="EMOJI_FOR_ACTIVATE_ITEM",
        value_type="str",
    )
    for key, value in decoded_dict.items():
        name_item = (
            await session.scalar(select(Item).where(Item.code_name == key))
        ).name_with_emoji
        value = EMOJI_FOR_ACTIVATE_ITEM if value["is_activate"] == True else ""
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
    size_items = await get_size_items_for_kb(session=session)
    return math.ceil(len(decoded_dict) / size_items)


async def get_status_item(items: str, code_name_item: str):
    decoded_dict: dict = json.loads(items)
    if decoded_dict.get(code_name_item):
        return decoded_dict[code_name_item]["is_activate"]
    return False


async def get_activated_items(session: AsyncSession, items: str):
    decoded_dict: dict = json.loads(items)
    activated_items = []
    for key, value in decoded_dict.items():
        if value["is_activate"] == True:
            emoji = await session.scalar(
                select(Item.emoji).where(Item.code_name == key)
            )
            activated_items.append(emoji)
    return activated_items


async def add_item(
    self: User, code_name_item: str, is_activate: bool = False, **kwargs
) -> None:
    decoded_dict: dict = json.loads(self.items)
    decoded_dict[code_name_item] = {"is_activate": is_activate, **kwargs}
    self.items = json.dumps(decoded_dict, ensure_ascii=False)


async def activate_item(
    self: User, code_name_item: str, is_active: bool = True
) -> None:
    decoded_dict: dict = json.loads(self.items)
    decoded_dict[code_name_item]["is_activate"] = is_active
    self.items = json.dumps(decoded_dict, ensure_ascii=False)


async def deactivate_all_items(self: User) -> None:
    decoded_dict: dict = json.loads(self.items)
    for key in decoded_dict:
        decoded_dict[key]["is_activate"] = False
    self.items = json.dumps(decoded_dict, ensure_ascii=False)


async def add_value_to_item(
    self: User, code_name_item: str, value_name: str, value: int
) -> None:
    decoded_dict: dict = json.loads(self.items)
    decoded_dict[code_name_item][value_name] = value
    self.items = json.dumps(decoded_dict, ensure_ascii=False)


async def get_value_from_item(items: str, code_name_item: str, value_name: str) -> str:
    decoded_dict: dict = json.loads(items)
    return decoded_dict[code_name_item].get(value_name)


async def get_values_from_item(items: str, code_name_item: str) -> dict | None:
    decoded_dict: dict = json.loads(items)
    return decoded_dict.get(code_name_item)
