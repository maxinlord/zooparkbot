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
    bonus: Mapped[int] = mapped_column(default=1)

    


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


class TransferMoney(Base):
    __tablename__ = "transfer_money"

    id_transfer: Mapped[str] = mapped_column(String(length=10))
    idpk_user: Mapped[int] = mapped_column()
    currency: Mapped[str] = mapped_column(String(length=10))
    one_piece_sum: Mapped[int] = mapped_column(BigInteger)
    pieces: Mapped[int] = mapped_column()
    used: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[bool] = mapped_column(default=False)

    



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
