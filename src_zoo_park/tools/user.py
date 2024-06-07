import json
from sqlalchemy import select
from db import Text, Button, Value, Unity, User
from init_db import _sessionmaker_for_func


async def add_to_currency(self: User, currency: str, amount: int) -> None:
    async with _sessionmaker_for_func() as session:
        if hasattr(self, currency):
            setattr(self, currency, getattr(self, currency) + amount)
        await session.commit()



async def get_currency(self: User, currency: str) -> int:
    match currency:
        case "rub":
            return self.rub
        case "usd":
            return self.usd
        case "paw_coins":
            return self.paw_coins


async def add_to_amount_expenses_currency(
    self: User, currency: str, amount: int
) -> None:
    async with _sessionmaker_for_func() as session:
        match currency:
            case "rub":
                self.amount_expenses_rub += amount
            case "usd":
                self.amount_expenses_usd += amount
            case "paw_coins":
                self.amount_expenses_paw_coins += amount
        await session.commit()


async def add_animal(self: User, code_name_animal: str, quantity: int) -> None:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(self.animals)
        if code_name_animal in decoded_dict:
            decoded_dict[code_name_animal] += quantity
        else:
            decoded_dict[code_name_animal] = quantity
        self.animals = json.dumps(decoded_dict, ensure_ascii=False)
        await session.commit()


async def activate_item(
    self: User, code_name_item: str, is_active: bool = True
) -> None:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(self.items)
        decoded_dict[code_name_item] = is_active
        self.items = json.dumps(decoded_dict, ensure_ascii=False)
        await session.commit()


async def deactivate_all_items(self: User) -> None:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(self.items)
        for key in decoded_dict:
            decoded_dict[key] = False
        self.items = json.dumps(decoded_dict, ensure_ascii=False)
        await session.commit()


async def get_status_item(self: User, code_name_item: str):
    decoded_dict: dict = json.loads(self.items)
    return decoded_dict[code_name_item]


async def add_aviary(self: User, code_name_aviary: str, quantity: int) -> None:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(self.aviaries)
        if code_name_aviary in decoded_dict:
            decoded_dict[code_name_aviary] += quantity
        else:
            decoded_dict[code_name_aviary] = quantity
        self.aviaries = json.dumps(decoded_dict, ensure_ascii=False)
        await session.commit()


async def get_total_number_animals(self: User) -> int:
    decoded_dict: dict = json.loads(self.animals)
    return sum(decoded_dict.values())


def get_numbers_animals(self: User) -> list[int]:
    decoded_dict: dict = json.loads(self.animals)
    return list(decoded_dict.values())


def get_dict_animals(self: User) -> dict:
    decoded_dict: dict = json.loads(self.animals)
    return decoded_dict
