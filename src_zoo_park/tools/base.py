import re
from sqlalchemy.ext.asyncio import AsyncSession
import string
import random
import tools


def gen_key(length):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


async def find_integers(text: str) -> int | None:
    numbers = re.sub(r"[^\d\s]", " ", text)
    integers = re.findall(r"\d+", numbers)
    return int("".join(integers)) if integers else None


async def fetch_and_parse_str_value(
    session: AsyncSession,
    value_name: str,
    func_to_element = int,
    sep: str = ",",
) -> list[any]:
    value_str = await tools.get_value(
        session=session,
        value_name=value_name,
        value_type="str",
    )
    return [func_to_element(v.strip()) for v in value_str.split(",")]
