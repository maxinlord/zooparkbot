from db import TransferMoney
from sqlalchemy.ext.asyncio import AsyncSession


async def in_used(session: AsyncSession, idpk_tr: int, idpk_user: int) -> bool:
    tr = await session.get(TransferMoney, idpk_tr)
    if not tr.used:
        return False
    if str(idpk_user) in tr.used:
        return True


async def add_user_to_used(session: AsyncSession, idpk_tr: int, idpk_user: int):
    tr = await session.get(TransferMoney, idpk_tr)
    if tr.used:
        tr.used += f", {idpk_user}"
    else:
        tr.used = f"{idpk_user}"
    await session.commit()
