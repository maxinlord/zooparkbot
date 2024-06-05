import json
from sqlalchemy import (
    BigInteger,
    Float,
    String,
    Text,
    DateTime,
)
from .base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id_user: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(length=64))
    nickname: Mapped[str] = mapped_column(String(length=64), nullable=True)
    date_reg: Mapped[str] = mapped_column(DateTime)
    id_referrer: Mapped[int] = mapped_column(BigInteger, nullable=True)
    referral_verification: Mapped[bool] = mapped_column(default=False)
    moves: Mapped[int] = mapped_column(default=0)
    history_moves: Mapped[str] = mapped_column(Text, default="{}")
    paw_coins: Mapped[int] = mapped_column(default=0)
    amount_expenses_paw_coins: Mapped[int] = mapped_column(default=0)
    rub: Mapped[int] = mapped_column(BigInteger, default=0)
    amount_expenses_rub: Mapped[int] = mapped_column(BigInteger, default=0)
    usd: Mapped[int] = mapped_column(BigInteger, default=0)
    amount_expenses_usd: Mapped[int] = mapped_column(BigInteger, default=0)
    animals: Mapped[str] = mapped_column(Text, default="{}")
    items: Mapped[str] = mapped_column(Text, default="{}")
    aviaries: Mapped[str] = mapped_column(Text, default="{}")
    current_unity: Mapped[str] = mapped_column(String(64), nullable=True)
    sub_on_chat: Mapped[bool] = mapped_column(default=False)
    sub_on_channel: Mapped[bool] = mapped_column(default=False)

    def get_currency(self, currency: str) -> int:
        dict_currencies = {
            "paw_coins": self.paw_coins,
            "rub": self.rub,
            "usd": self.usd,
        }
        return dict_currencies[currency]

    def add_to_amount_expenses_currency(self, currency: str, amount: int) -> None:
        dict_currencies = {
            "paw_coins": self.amount_expenses_paw_coins,
            "rub": self.amount_expenses_rub,
            "usd": self.amount_expenses_usd,
        }
        dict_currencies[currency] += amount

    def add_to_currency(self, currency: str, amount: int) -> None:
        dict_currencies = {
            "paw_coins": self.paw_coins,
            "rub": self.rub,
            "usd": self.usd,
        }
        dict_currencies[currency] += amount

    def add_animal(self, code_name_animal: str, quantity: int) -> None:
        decoded_dict: dict = json.loads(self.animals)
        if code_name_animal in decoded_dict:
            decoded_dict[code_name_animal] += quantity
        else:
            decoded_dict[code_name_animal] = quantity
        self.animals = json.dumps(decoded_dict, ensure_ascii=False)

    def add_item(self, code_name_item: str, is_activate: bool = False) -> None:
        decoded_dict: dict = json.loads(self.items)
        decoded_dict[code_name_item] = is_activate
        self.items = json.dumps(decoded_dict, ensure_ascii=False)

    def activate_item(self, code_name_item: str, is_active: bool = True) -> None:
        decoded_dict: dict = json.loads(self.items)
        decoded_dict[code_name_item] = is_active
        self.items = json.dumps(decoded_dict, ensure_ascii=False)

    def deactivate_all_items(self) -> None:
        decoded_dict: dict = json.loads(self.items)
        for key in decoded_dict:
            decoded_dict[key] = False
        self.items = json.dumps(decoded_dict, ensure_ascii=False)

    def get_status_item(self, code_name_item: str):
        decoded_dict: dict = json.loads(self.items)
        return decoded_dict[code_name_item]

    def add_aviary(self, code_name_aviary: str, quantity: int) -> None:
        decoded_dict: dict = json.loads(self.aviaries)
        if code_name_aviary in decoded_dict:
            decoded_dict[code_name_aviary] += quantity
        else:
            decoded_dict[code_name_aviary] = quantity
        self.aviaries = json.dumps(decoded_dict, ensure_ascii=False)

    def get_total_number_animals(self) -> int:
        decoded_dict: dict = json.loads(self.animals)
        return sum(decoded_dict.values())

    def get_numbers_animals(self) -> list[int]:
        decoded_dict: dict = json.loads(self.animals)
        return list(decoded_dict.values())

    def get_dict_animals(self) -> dict:
        decoded_dict: dict = json.loads(self.animals)
        return decoded_dict


class Unity(Base):
    __tablename__ = "unity"

    idpk_user: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column(String(length=64))
    members: Mapped[str] = mapped_column(Text, default="{}")
    level: Mapped[int] = mapped_column(default=0)

    def add_member(self, idpk_member: int, rule: str = "member") -> None:
        decoded_dict: dict = json.loads(self.members)
        decoded_dict[idpk_member] = rule
        self.members = json.dumps(decoded_dict, ensure_ascii=False)

    def remove_member(self, idpk_member: str) -> None:
        decoded_dict: dict = json.loads(self.members)
        if idpk_member in decoded_dict:
            del decoded_dict[idpk_member]
        self.members = json.dumps(decoded_dict, ensure_ascii=False)

    def remove_first_member(self) -> int:
        decoded_dict: dict = json.loads(self.members)
        key = 0
        if decoded_dict:
            key = list(decoded_dict.keys())[0]
            del decoded_dict[key]
        self.members = json.dumps(decoded_dict, ensure_ascii=False)
        return int(key)

    def get_number_members(self) -> int:
        """Возвращает количество участников вместе с владельцем"""
        decoded_dict: dict = json.loads(self.members)
        return len(decoded_dict) + 1

    def get_members_idpk(self) -> list[str]:
        decoded_dict: dict = json.loads(self.members)
        return list(decoded_dict.keys()) + [self.idpk_user]


class RequestToUnity(Base):
    __tablename__ = "requests_to_unity"

    idpk_user: Mapped[int] = mapped_column()
    idpk_unity_owner: Mapped[int] = mapped_column()
    date_request: Mapped[str] = mapped_column(DateTime)
    date_request_end: Mapped[str] = mapped_column(DateTime)


class Item(Base):
    __tablename__ = "items"

    code_name: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(length=64))
    description: Mapped[str] = mapped_column(String(length=4096))
    price: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(String(length=64))
    value: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(default=0)


class Animal(Base):
    __tablename__ = "animals"

    code_name: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(length=64))
    description: Mapped[str] = mapped_column(String(length=4096))
    price: Mapped[int] = mapped_column(BigInteger)
    income: Mapped[int] = mapped_column(BigInteger)


class Aviary(Base):
    __tablename__ = "aviaries"

    name: Mapped[str] = mapped_column(String(length=64))
    code_name: Mapped[str] = mapped_column(String(length=64))
    size: Mapped[int] = mapped_column()
    price: Mapped[int] = mapped_column()


class RandomMerchant(Base):
    __tablename__ = "random_merchants"

    id_user: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(length=64))
    code_name_animal: Mapped[str] = mapped_column(String(length=64))
    discount: Mapped[int] = mapped_column()
    price_with_discount: Mapped[int] = mapped_column()
    quantity_animals: Mapped[int] = mapped_column()
    price: Mapped[int] = mapped_column()
    first_offer_bought: Mapped[bool] = mapped_column(default=False)


class Text(Base):
    __tablename__ = "texts"

    name: Mapped[str] = mapped_column(String(length=100))  # Название текста
    text: Mapped[str] = mapped_column(
        String(length=4096), default="текст не задан"
    )  # Текст


class Button(Base):
    __tablename__ = "buttons"

    name: Mapped[str] = mapped_column(String(length=100))  # Название кнопки
    text: Mapped[str] = mapped_column(
        String(length=64), default="кнопка"
    )  # Текст кнопки


class BlackList(Base):
    __tablename__ = "blacklist"

    id_user: Mapped[int] = mapped_column(BigInteger)  # Идентификатор пользователя


class Value(Base):
    __tablename__ = "values"

    name: Mapped[str] = mapped_column(String(length=100))  # Название значения
    value_int: Mapped[int] = mapped_column(default=0)  # Значение целое
    value_str: Mapped[str] = mapped_column(
        String(length=4096), default="не установлено"
    )  # Значение строка


class Photo(Base):
    __tablename__ = "photos"

    name: Mapped[str] = mapped_column(String(length=30))  # Название фото
    photo_id: Mapped[str] = mapped_column(String(length=100))  # Идентификатор фото
