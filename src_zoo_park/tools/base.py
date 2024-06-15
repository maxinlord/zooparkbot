from sqlalchemy.ext.asyncio import AsyncSession
import string
import random
import tools


def gen_key(length):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


async def get_rates_calculator(session: AsyncSession):
    rates = await tools.get_value(
        session=session, value_name="RATES_CALCULATOR", value_type="str"
    )
    rates = [i.strip() for i in rates.split(",")]
    return rates
