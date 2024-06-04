import html
import re
from sqlalchemy import desc, select
from init_db import _sessionmaker_for_func
from db import Unity, Value, User, Animal
from tools import income, get_text_message


async def shorten_whitespace_name_unity(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip()


async def has_special_characters_name(name: str) -> str | None:
    # Паттерн для поиска специальных символов
    pattern = r"[^a-zA-Zа-яА-Я0-9\-\ ]"
    special_chars = re.findall(pattern, html.unescape(name))
    return "".join(special_chars) if special_chars else None


async def is_unique_name(name: str) -> bool:
    async with _sessionmaker_for_func() as session:
        unity_name = await session.scalars(select(Unity.name))
        unity_name = [name.lower() for name in unity_name.all() if name is not None]
        if name.lower() in unity_name:
            return False
    return True


async def get_row_unity_for_kb():
    async with _sessionmaker_for_func() as session:
        row = await session.scalar(
            select(Value.value_int).where(Value.name == "ROW_UNITY_FOR_KB")
        )
    return row


async def get_size_unity_for_kb():
    async with _sessionmaker_for_func() as session:
        size = await session.scalar(
            select(Value.value_int).where(Value.name == "SIZE_UNITY_FOR_KB")
        )
    return size


async def get_unity_name_and_idpk() -> list[tuple[str, int]]:
    async with _sessionmaker_for_func() as session:
        r = await session.execute(select(Unity.name, Unity.idpk_user))
        return r.all()


async def count_page_unity() -> int:
    async with _sessionmaker_for_func() as session:
        size = await get_size_unity_for_kb()
        r = await session.scalars(select(Unity.name))
        len_unity = len(r.all())
        remains = len_unity % size
        return len_unity // size + (1 if remains else 0)


async def check_condition_1st_lvl(unity: Unity) -> bool:
    async with _sessionmaker_for_func() as session:
        AMOUNT_MEMBERS_1ST_LVL = await session.scalar(
            select(Value.value_int).where(Value.name == "AMOUNT_MEMBERS_1ST_LVL")
        )
        return unity.get_number_members() >= AMOUNT_MEMBERS_1ST_LVL


async def check_condition_2nd_lvl(unity: Unity) -> bool:
    async with _sessionmaker_for_func() as session:
        AMOUNT_INCOME_2ND_LVL = await session.scalar(
            select(Value.value_int).where(Value.name == "AMOUNT_INCOME_2ND_LVL")
        )
        AMOUNT_ANIMALS_2ND_LVL = await session.scalar(
            select(Value.value_int).where(Value.name == "AMOUNT_ANIMALS_2ND_LVL")
        )
        total_income = 0
        users = [
            await session.get(User, int(idpk)) for idpk in unity.get_members_idpk()
        ]
        total_income = sum([await income(user=user) for user in users])
        if total_income < AMOUNT_INCOME_2ND_LVL:
            return False
        return all(
            num_animal >= AMOUNT_ANIMALS_2ND_LVL
            for user in users
            for num_animal in user.get_numbers_animals()
        )


async def check_condition_3rd_lvl(unity: Unity) -> bool:
    async with _sessionmaker_for_func() as session:
        AMOUNT_INCOME_3RD_LVL = await session.scalar(
            select(Value.value_int).where(Value.name == "AMOUNT_INCOME_3RD_LVL")
        )
        AMOUNT_ANIMALS_3RD_LVL = await session.scalar(
            select(Value.value_int).where(Value.name == "AMOUNT_ANIMALS_3RD_LVL")
        )
        AMOUNT_MEMBERS_3RD_LVL = await session.scalar(
            select(Value.value_int).where(Value.name == "AMOUNT_MEMBERS_3RD_LVL")
        )
        if unity.get_number_members() < AMOUNT_MEMBERS_3RD_LVL:
            return False
        total_income = 0
        users = [
            await session.get(User, int(idpk)) for idpk in unity.get_members_idpk()
        ]
        total_income = sum([await income(user=user) for user in users])
        if total_income < AMOUNT_INCOME_3RD_LVL:
            return False
        return all(
            num_animal >= AMOUNT_ANIMALS_3RD_LVL
            for user in users
            for num_animal in user.get_numbers_animals()
        )


async def get_data_by_lvl_unity(lvl: int) -> dict:
    async with _sessionmaker_for_func() as session:
        data = {"lvl": lvl}
        match lvl:
            case 0:
                data["amount_members"] = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "AMOUNT_MEMBERS_1ST_LVL"
                    )
                )
                data["next_lvl"] = 1
            case 1:
                data["amount_income"] = await session.scalar(
                    select(Value.value_int).where(Value.name == "AMOUNT_INCOME_2ND_LVL")
                )
                data["amount_animals"] = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "AMOUNT_ANIMALS_2ND_LVL"
                    )
                )
                data["bonus_add_to_income"] = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "BONUS_ADD_TO_INCOME_1ST_LVL"
                    )
                )
                data["next_lvl"] = 2
            case 2:
                data["amount_income"] = await session.scalar(
                    select(Value.value_int).where(Value.name == "AMOUNT_INCOME_3RD_LVL")
                )
                data["amount_animals"] = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "AMOUNT_ANIMALS_3RD_LVL"
                    )
                )
                data["amount_members"] = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "AMOUNT_MEMBERS_3RD_LVL"
                    )
                )
                data["bonus_add_to_income"] = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "BONUS_ADD_TO_INCOME_1ST_LVL"
                    )
                )
                data["bonus_discount_for_animal"] = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "BONUS_DISCOUNT_FOR_ANIMAL_2ND_LVL"
                    )
                )
                data["next_lvl"] = 3
            case 3:
                data["bonus_add_to_income"] = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "BONUS_ADD_TO_INCOME_3RD_LVL"
                    )
                )
                data["bonus_discount_for_animal"] = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "BONUS_DISCOUNT_FOR_ANIMAL_3RD_LVL"
                    )
                )
    return data


async def get_row_unity_members():
    async with _sessionmaker_for_func() as session:
        row = await session.scalar(
            select(Value.value_int).where(Value.name == "ROW_UNITY_MEMBERS")
        )
    return row


async def get_size_unity_members():
    async with _sessionmaker_for_func() as session:
        size = await session.scalar(
            select(Value.value_int).where(Value.name == "SIZE_UNITY_MEMBERS")
        )
    return size


async def count_page_unity_members(idpk_unity: int) -> int:
    async with _sessionmaker_for_func() as session:
        size = await get_size_unity_members()
        unity = await session.get(Unity, idpk_unity)
        len_unity = unity.get_number_members()
        remains = len_unity % size
        return len_unity // size + (1 if remains else 0)


async def get_members_name_and_idpk(idpk_unity: int) -> list[tuple[str, int]]:
    async with _sessionmaker_for_func() as session:
        unity = await session.get(Unity, idpk_unity)
        members_idpk = unity.get_members_idpk()
        members = [await session.get(User, idpk) for idpk in members_idpk]
        members_name = [member.nickname for member in members]
        data = list(zip(members_name, members_idpk))
    return data


async def factory_text_unity_top() -> str:
    async with _sessionmaker_for_func() as session:
        unitys = await session.scalars(select(Unity))
        unitys = unitys.all()
        unitys_income = [await count_income_unity(unity=unity) for unity in unitys]
        ls = list(zip(unitys, unitys_income))
        ls.sort(key=lambda x: x[1], reverse=True)
        text = ""
        for counter, ls_obj in enumerate(ls, start=1):
            unity = ls_obj[0]
            i = ls_obj[1]
            text += (
                await get_text_message(
                    "pattern_line_top_unity", n=unity.name, i=i, c=counter
                )
                + "\n"
            )
        return text


async def count_income_unity(unity: Unity) -> int:
    async with _sessionmaker_for_func() as session:
        total_income = 0
        users = [
            await session.get(User, int(idpk)) for idpk in unity.get_members_idpk()
        ]
        total_income = sum([await income(user=user) for user in users])
        return total_income
