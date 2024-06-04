from sqlalchemy import select
from db import Text, Button, Value
from init_db import _sessionmaker_for_func


async def get_rate_bank() -> int:
    async with _sessionmaker_for_func() as session:
        rub_usd = await session.scalar(select(Value.value_int).where(Value.name == 'RATE_RUB_USD'))
        return rub_usd