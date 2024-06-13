from collections import defaultdict
import html
import re
from sqlalchemy import select
from init_db import _sessionmaker_for_func
from db import Unity, User
import tools
from sqlalchemy.ext.asyncio import AsyncSession


async def shorten_whitespace_name_unity(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip()


async def has_special_characters_name(name: str) -> str | None:
    # Паттерн для поиска специальных символов
    pattern = r"[^a-zA-Zа-яА-Я0-9\-\ ]"
    special_chars = re.findall(pattern, html.unescape(name))
    return "".join(special_chars) if special_chars else None


async def is_unique_name(session: AsyncSession, nickname: str) -> bool:
    users_nickname = await session.scalars(select(User.nickname))
    users_nickname = [
        nickname.lower() for nickname in users_nickname.all() if nickname is not None
    ]
    return nickname.lower() not in users_nickname


async def get_row_unity_for_kb(session: AsyncSession):
    row = await tools.get_value(session=session, value_name="ROW_UNITY_FOR_KB")
    return row


async def get_size_unity_for_kb(session: AsyncSession):
    size = await tools.get_value(session=session, value_name="SIZE_UNITY_FOR_KB")
    return size


async def get_unity_name_and_idpk(session: AsyncSession) -> list[tuple[str, int]]:
    r = await session.execute(select(Unity.name, Unity.idpk_user))
    return r.all()


async def count_page_unity(
    session: AsyncSession,
) -> int:
    size = await get_size_unity_for_kb(session=session)
    r = await session.scalars(select(Unity.name))
    len_unity = len(r.all())
    remains = len_unity % size
    return len_unity // size + (1 if remains else 0)


async def check_condition_1st_lvl(session: AsyncSession, unity: Unity) -> bool:
    AMOUNT_MEMBERS_1ST_LVL = await tools.get_value(
        session=session, value_name="AMOUNT_MEMBERS_1ST_LVL"
    )
    return unity.get_number_members() >= AMOUNT_MEMBERS_1ST_LVL


async def get_data_by_lvl_unity(session: AsyncSession, lvl: int) -> dict:
    data = {"lvl": lvl}
    match lvl:
        case 0:
            data["amount_members"] = await tools.get_value(
                session=session, value_name="AMOUNT_MEMBERS_1ST_LVL"
            )
            data["next_lvl"] = 1
        case 1:
            data["amount_income"] = await tools.get_value(
                session=session, value_name="AMOUNT_INCOME_2ND_LVL"
            )
            data["amount_animals"] = await tools.get_value(
                session=session, value_name="AMOUNT_ANIMALS_2ND_LVL"
            )
            data["bonus_add_to_income"] = await tools.get_value(
                session=session, value_name="BONUS_ADD_TO_INCOME_1ST_LVL"
            )
            data["next_lvl"] = 2
        case 2:
            data["amount_income"] = await tools.get_value(
                session=session, value_name="AMOUNT_INCOME_3RD_LVL"
            )
            data["amount_animals"] = await tools.get_value(
                session=session, value_name="AMOUNT_ANIMALS_3RD_LVL"
            )
            data["amount_members"] = await tools.get_value(
                session=session, value_name="AMOUNT_MEMBERS_3RD_LVL"
            )
            data["bonus_add_to_income"] = await tools.get_value(
                session=session, value_name="BONUS_ADD_TO_INCOME_2ND_LVL"
            )
            data["bonus_discount_for_animal"] = await tools.get_value(
                session=session, value_name="BONUS_DISCOUNT_FOR_ANIMAL_2ND_LVL"
            )
            data["next_lvl"] = 3
        case 3:
            data["bonus_add_to_income"] = await tools.get_value(
                session=session, value_name="BONUS_ADD_TO_INCOME_3RD_LVL"
            )
            data["bonus_discount_for_animal"] = await tools.get_value(
                session=session, value_name="BONUS_DISCOUNT_FOR_ANIMAL_3RD_LVL"
            )
    return data


async def get_row_unity_members(session: AsyncSession):
    row = await tools.get_value(session=session, value_name="ROW_UNITY_MEMBERS")
    return row


async def get_size_unity_members(session: AsyncSession):
    size = await tools.get_value(session=session, value_name="SIZE_UNITY_MEMBERS")
    return size


async def count_page_unity_members(session: AsyncSession, idpk_unity: int) -> int:
    size = await get_size_unity_members()
    unity = await session.get(Unity, idpk_unity)
    len_unity = unity.get_number_members()
    remains = len_unity % size
    return len_unity // size + (1 if remains else 0)


async def get_members_name_and_idpk(
    session: AsyncSession, idpk_unity: int
) -> list[tuple[str, int]]:
    unity = await session.get(Unity, idpk_unity)
    members_idpk = unity.get_members_idpk()
    members = [await session.get(User, idpk) for idpk in members_idpk]
    members_name = [member.nickname for member in members]
    data = list(zip(members_name, members_idpk))
    return data


async def get_top_unity_by_animal(session: AsyncSession) -> tuple[int, dict]:
    table_for_compare = {}

    # Fetch all unities and users in a single query
    unites = await session.scalars(select(Unity))
    unites = unites.all()
    user_ids = [int(idpk) for unity in unites for idpk in unity.get_members_idpk()]
    users = await session.execute(select(User).where(User.idpk.in_(user_ids)))
    users = {user.idpk: user for user in users.scalars().all()}

    for unity in unites:
        member_ids = unity.get_members_idpk()
        animals = defaultdict(int)
        for idpk in member_ids:
            user = users[int(idpk)]
            animals_user = await tools.get_dict_animals(self=user)
            for animal_name, num_animal in animals_user.items():
                animals[animal_name] += num_animal
        max_animal = max(animals, key=animals.get)
        table_for_compare[unity.idpk] = {max_animal: animals[max_animal]}
    top_unity = max(
        table_for_compare, key=lambda x: next(iter(table_for_compare[x].values()))
    )
    return int(top_unity), table_for_compare[top_unity]


async def check_condition_2nd_lvl(session: AsyncSession, unity: Unity) -> bool:
    async with _sessionmaker_for_func() as session:
        AMOUNT_INCOME_2ND_LVL = await tools.tools.get_value(
            session=session, value_name="AMOUNT_INCOME_2ND_LVL"
        )
        AMOUNT_ANIMALS_2ND_LVL = await tools.tools.get_value(
            session=session, value_name="AMOUNT_ANIMALS_2ND_LVL"
        )
        total_income = 0
        users = [
            await session.get(User, int(idpk)) for idpk in unity.get_members_idpk()
        ]
        total_income = sum(
            [await tools.income_(session=session, user=user) for user in users]
        )
        if total_income < AMOUNT_INCOME_2ND_LVL:
            return False
        return all(
            num_animal >= AMOUNT_ANIMALS_2ND_LVL
            for user in users
            for num_animal in await tools.get_numbers_animals(user)
        )


async def check_condition_3rd_lvl(session: AsyncSession, unity: Unity) -> bool:
    async with _sessionmaker_for_func() as session:
        AMOUNT_INCOME_3RD_LVL = await tools.tools.get_value(
            session=session, value_name="AMOUNT_INCOME_3RD_LVL"
        )
        AMOUNT_ANIMALS_3RD_LVL = await tools.tools.get_value(
            session=session, value_name="AMOUNT_ANIMALS_3RD_LVL"
        )
        AMOUNT_MEMBERS_3RD_LVL = await tools.tools.get_value(
            session=session, value_name="AMOUNT_MEMBERS_3RD_LVL"
        )
        if unity.get_number_members() < AMOUNT_MEMBERS_3RD_LVL:
            return False
        total_income = 0
        users = [
            await session.get(User, int(idpk)) for idpk in unity.get_members_idpk()
        ]
        total_income = sum(
            [await tools.income_(session=session, user=user) for user in users]
        )
        if total_income < AMOUNT_INCOME_3RD_LVL:
            return False
        return all(
            num_animal >= AMOUNT_ANIMALS_3RD_LVL
            for user in users
            for num_animal in await tools.get_numbers_animals(user)
        )

async def count_income_unity(unity: Unity) -> int:
    async with _sessionmaker_for_func() as session:
        total_income = 0
        users = [
            await session.get(User, int(idpk)) for idpk in unity.get_members_idpk()
        ]
        total_income = sum(
            [await tools.income_(session=session, user=user) for user in users]
        )
        return total_income
