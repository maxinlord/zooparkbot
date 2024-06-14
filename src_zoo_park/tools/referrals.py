from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from sqlalchemy import select


async def get_referrals(session: AsyncSession, user: User):
    r = await session.scalars(select(User.idpk).where(User.id_referrer == user.idpk))
    return len(r.all())
