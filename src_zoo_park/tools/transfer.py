import asyncio
import json
from sqlalchemy import select
from db import User, Value, Aviary, Animal, Item, TransferMoney
from init_db import _sessionmaker_for_func
import random
from config import rarities


async def in_used(idpk_tr: int, idpk_user: int) -> bool:
    async with _sessionmaker_for_func() as session:
        tr = await session.get(TransferMoney, idpk_tr)
        if not tr.used:
            return False
        if str(idpk_user) in tr.used:
            return True


async def add_user_to_used(idpk_tr: int, idpk_user: int):
    async with _sessionmaker_for_func() as session:
        tr = await session.get(TransferMoney, idpk_tr)
        if tr.used:
            tr.used += f", {idpk_user}"
        else:
            tr.used = f"{idpk_user}"
        await session.commit()
