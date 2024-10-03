from db import User
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_referrals(session: AsyncSession, user: User):
    r = await session.scalars(select(User.idpk).where(User.id_referrer == user.idpk))
    return len(r.all())


async def get_verify_referrals(session: AsyncSession, user: User):
    r = await session.scalars(
        select(User.idpk).where(
            and_(
                User.id_referrer == user.idpk,
                User.referral_verification == True,  # noqa: E712
            )
        )
    )
    return len(r.all())
