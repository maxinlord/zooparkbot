from sqlalchemy import (
    BigInteger,
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


class Animal(Base):
    __tablename__ = "animals"

    code_name: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(length=64))
    description: Mapped[str] = mapped_column(String(length=4096))
    price: Mapped[int] = mapped_column(BigInteger)
    income: Mapped[int] = mapped_column(BigInteger)
    images: Mapped[str] = mapped_column(String(length=300))  # for id 3 image


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
