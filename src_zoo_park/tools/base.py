import re
from sqlalchemy.ext.asyncio import AsyncSession
import string
import random
import tools


def gen_key(length):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


multipliers = {"k": 10**3, "к": 10**3, "m": 10**6, "м": 10**6, "b": 10**9, "б": 10**9}


async def remove_punctuation_and_spaces(text: str) -> str:
    # Регулярное выражение для замены всех знаков и пробелов на пустую строку
    return re.sub(r"[^\w]", "", text)


async def find_integers(text: str) -> int | None:
    num: str = await remove_punctuation_and_spaces(text)

    if not num:
        return None
    elif num.isdigit():
        return int(num)
    elif num.isalpha():
        return None

    match_num = re.search(r"\d+", num)

    number = int(match_num.group())
    num = num[match_num.end() :]
    suffix = re.search(r"[^\W\d_]+", num)

    suffix = (suffix.group()).lower()

    if len(suffix) > 6:
        return None

    for s in suffix:
        if s not in multipliers:
            continue
        number *= multipliers[s]
    return int(number)


async def fetch_and_parse_str_value(
    session: AsyncSession,
    value_name: str,
    func_to_element=int,
    sep: str = ",",
) -> list[any]:
    value_str = await tools.get_value(
        session=session,
        value_name=value_name,
        value_type="str",
    )
    return [func_to_element(v.strip()) for v in value_str.split(",")]
