import json

from sqlalchemy import or_, select
from db import User
from sqlalchemy.ext.asyncio import AsyncSession


async def add_to_currency(self: User, currency: str, amount: int) -> None:
    if hasattr(self, currency):
        setattr(self, currency, getattr(self, currency) + amount)


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
    match currency:
        case "rub":
            self.amount_expenses_rub += amount
        case "usd":
            self.amount_expenses_usd += amount
        case "paw_coins":
            self.amount_expenses_paw_coins += amount


async def fetch_users_for_top(session: AsyncSession, idpk_user: int) -> list[User]:
    users = await session.scalars(
        select(User).where(or_(User.animals != "{}", User.idpk == idpk_user))
    )
    return users.all()