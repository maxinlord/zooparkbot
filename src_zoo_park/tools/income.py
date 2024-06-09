import asyncio
from collections import defaultdict
import random
from sqlalchemy import select
from db import Value, Item, Aviary, User, Animal, Unity, Item
from init_db import _sessionmaker_for_func
import json
from config import rarities
from tools import get_text_message

from sqlalchemy.ext.asyncio import AsyncSession


async def income_(user: User):
    unity_idpk = int(user.current_unity.split(":")[-1]) if user.current_unity else None
    animals: dict = json.loads(user.animals)
    income = await income_from_animal(animals, unity_idpk)
    if unity_idpk:
        unity_data = await get_unity_data_for_income(unity_idpk)
        if unity_data["lvl"] in [1, 2, 3]:
            income *= 1 + (unity_data["bonus"] / 100)
    return int(income)


async def _get_income_animal(animal: Animal, unity_idpk: int | None, bonus: int):
    async with _sessionmaker_for_func() as session:
        if unity_idpk:
            unity_idpk_top, animal_top = await get_top_unity_by_animal()
            if (
                unity_idpk_top == unity_idpk
                and animal.code_name == list(animal_top.keys())[0]
            ):
                animal_income = animal.income * (1 + (bonus / 100))
                return int(animal_income)
        return animal.income


async def income_from_animal(animals: dict, unity_idpk: int):
    income = 0
    async with _sessionmaker_for_func() as session:
        bonus = await session.scalar(
            select(Value.value_int).where(Value.name == "BONUS_FOR_AMOUNT_ANIMALS")
        )
        for animal, quantity in animals.items():
            animal = await session.scalar(
                select(Animal).where(Animal.code_name == animal)
            )
            animal_income = await _get_income_animal(
                animal=animal, unity_idpk=unity_idpk, bonus=bonus
            )
            income += animal_income * quantity
    return income


async def get_unity_data_for_income(idpk_unity: int):
    async with _sessionmaker_for_func() as session:
        unity = await session.get(Unity, idpk_unity)
        data = {"lvl": unity.level}
        if unity.level in [1, 2]:
            data["bonus"] = await session.scalar(
                select(Value.value_int).where(
                    Value.name == "BONUS_ADD_TO_INCOME_1ST_LVL"
                )
            )
        elif unity.level == 3:
            data["bonus"] = await session.scalar(
                select(Value.value_int).where(
                    Value.name == "BONUS_ADD_TO_INCOME_3RD_LVL"
                )
            )
    return data


async def get_top_unity_by_animal() -> tuple[int, dict]:
    table_for_compare = {}
    async with _sessionmaker_for_func() as session:
        unitys = await session.scalars(select(Unity))
        unitys = unitys.all()
        for unity in unitys:
            member_ids = unity.get_members_idpk()
            animals = defaultdict(int)
            for idpk in member_ids:
                user = await session.get(User, int(idpk))
                animals_user = await get_dict_animals(self=user)
                for animal_name, num_animal in animals_user.items():
                    animals[animal_name] += num_animal
            max_animal = max(animals, key=animals.get)
            table_for_compare[unity.idpk] = {max_animal: animals[max_animal]}
        top_unity = max(
            table_for_compare, key=lambda x: next(iter(table_for_compare[x].values()))
        )
        return int(top_unity), table_for_compare[top_unity]


async def get_dict_animals(self: User) -> dict:
    decoded_dict: dict = json.loads(self.animals)
    return decoded_dict


async def get_income_animal(animal: Animal, unity_idpk: int):
    async with _sessionmaker_for_func() as session:
        if unity_idpk:
            unity_idpk_top, animal_top = await get_top_unity_by_animal()
            if (
                unity_idpk_top == unity_idpk
                and animal.code_name == list(animal_top.keys())[0]
            ):
                bonus = await session.scalar(
                    select(Value.value_int).where(
                        Value.name == "BONUS_FOR_AMOUNT_ANIMALS"
                    )
                )
                animal_income = animal.income * (1 + (bonus / 100))
                return int(animal_income)
        return animal.income


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
        total_income = sum([await income_(user=user) for user in users])
        if total_income < AMOUNT_INCOME_2ND_LVL:
            return False
        return all(
            num_animal >= AMOUNT_ANIMALS_2ND_LVL
            for user in users
            for num_animal in await get_numbers_animals(user)
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
        total_income = sum([await income_(user=user) for user in users])
        if total_income < AMOUNT_INCOME_3RD_LVL:
            return False
        return all(
            num_animal >= AMOUNT_ANIMALS_3RD_LVL
            for user in users
            for num_animal in await get_numbers_animals(user)
        )


def get_numbers_animals(self: User) -> list[int]:
    decoded_dict: dict = json.loads(self.animals)
    return list(decoded_dict.values())


async def count_income_unity(unity: Unity) -> int:
    async with _sessionmaker_for_func() as session:
        total_income = 0
        users = [
            await session.get(User, int(idpk)) for idpk in unity.get_members_idpk()
        ]
        total_income = sum([await income_(user=user) for user in users])
        return total_income


async def fetch_and_parse(session, name, parse_func):
    value_str = await session.scalar(select(Value.value_str).where(Value.name == name))
    return [parse_func(v.strip()) for v in value_str.split(",")]


async def handle_rub_bonus(user, session):
    income = await income_(user)
    if income == 0:
        income = 12
    income_for_3_min = income * 180
    rub_to_add = random.randint(income_for_3_min // 3, income_for_3_min)
    user.rub += rub_to_add
    return {"rub_to_add": rub_to_add}


async def handle_usd_bonus(user, session):
    weights = await fetch_and_parse(session, "WEIGHTS_FOR_BONUS_USD", float)
    types_usd_bonus = await fetch_and_parse(session, "TYPES_USD_BONUS", int)
    usd_to_add = random.choices(population=types_usd_bonus, weights=weights)[0]
    user.usd += usd_to_add
    return {"usd_to_add": usd_to_add}


async def handle_aviary_bonus(user, session):
    types_aviaries = list(await session.scalars(select(Aviary.code_name)))
    aviary_to_add = random.choice(types_aviaries)
    amount_to_add = random.randint(1, 5)
    await add_aviary(self=user, code_name_aviary=aviary_to_add, quantity=amount_to_add)
    return {"aviary_to_add": aviary_to_add, "amount_to_add": amount_to_add}


async def add_aviary(self: User, code_name_aviary: str, quantity: int) -> None:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(self.aviaries)
        if code_name_aviary in decoded_dict:
            decoded_dict[code_name_aviary] += quantity
        else:
            decoded_dict[code_name_aviary] = quantity
        self.aviaries = json.dumps(decoded_dict, ensure_ascii=False)
        await session.commit()


async def handle_animal_bonus(user: User, session):
    animal = await _get_random_animal(session=session, user_animals=user.animals)
    amount_to_add = random.randint(
        1,
        await _get_remain_seats(
            user.aviaries, await get_total_number_animals(self=user)
        ),
    )
    await add_animal(
        self=user,
        code_name_animal=animal.code_name,
        quantity=amount_to_add,
    )
    return {"animal_to_add": animal.name, "amount_to_add": amount_to_add}


async def add_animal(self: User, code_name_animal: str, quantity: int) -> None:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(self.animals)
        if code_name_animal in decoded_dict:
            decoded_dict[code_name_animal] += quantity
        else:
            decoded_dict[code_name_animal] = quantity
        self.animals = json.dumps(decoded_dict, ensure_ascii=False)
        await session.commit()


async def get_total_number_animals(self: User) -> int:
    decoded_dict: dict = json.loads(self.animals)
    return sum(decoded_dict.values())


async def handle_item_bonus(user: User, session):
    items = list(await session.scalars(select(Item)))
    item_to_add: Item = random.choice(items)
    if item_to_add.code_name in user.items:
        amount = item_to_add.price // 2
        dict_currencies = {
            "paw_coins": user.paw_coins,
            "rub": user.rub,
            "usd": user.usd,
        }
        dict_currencies[item_to_add.currency] += amount
        return {f"{item_to_add.currency}_to_add": amount}
    await add_item(self=user, code_name_item=item_to_add.code_name)
    return {"item_to_add": item_to_add.name}


async def add_item(self: User, code_name_item: str, is_activate: bool = False) -> None:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(self.items)
        decoded_dict[code_name_item] = is_activate
        self.items = json.dumps(decoded_dict, ensure_ascii=False)
        await session.commit()


async def bonus_(user: User):
    async with _sessionmaker_for_func() as session:
        types_bonus = ["rub", "usd", "aviary", "animal", "item"]
        weights = await fetch_and_parse(session, "WEIGHTS_FOR_BONUS", float)
        bonus_type = random.choices(population=types_bonus, weights=weights)[0]
        handlers = {
            "rub": handle_rub_bonus,
            "usd": handle_usd_bonus,
            "aviary": handle_aviary_bonus,
            "animal": handle_animal_bonus,
            "item": handle_item_bonus,
        }
        data_about_bonus = {bonus_type: await handlers[bonus_type](user, session)}
        await session.commit()
    return data_about_bonus


async def _get_random_animal(session: AsyncSession, user_animals: str) -> Animal:
    dict_animals: dict = json.loads(user_animals)
    if not dict_animals:
        r = await session.scalar(
            select(Value.value_str).where(Value.name == "START_ANIMALS_FOR_RMERCHANT")
        )
        c_names = [c_name.strip() for c_name in r.split(",")]
    else:
        c_names = [c_name.split("_")[0] for c_name in dict_animals]
    animal_name = random.choice(c_names)
    rarity = random.choices(
        population=rarities,
        weights=await _get_weights(),
    )
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == animal_name + rarity[0])
    )
    return animal


async def _get_weights() -> list:
    async with _sessionmaker_for_func() as session:
        w_str = await session.scalar(
            select(Value.value_str).where(Value.name == "WEIGHTS_FOR_RANDOM_MERCHANT")
        )
        weights = [float(w.strip()) for w in w_str.split(",")]
        return weights


async def _get_total_number_seats(aviaries: str) -> int:
    async with _sessionmaker_for_func() as session:
        decoded_dict: dict = json.loads(aviaries)
        all_seats = 0
        for key, value in decoded_dict.items():
            all_seats += (
                await session.scalar(select(Aviary.size).where(Aviary.code_name == key))
                * value
            )
        return all_seats


async def _get_remain_seats(aviaries: str, amount_animals: int) -> int:
    all_seats = await _get_total_number_seats(aviaries)
    return all_seats - amount_animals


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


async def factory_text_main_top(idpk_user: int) -> str:
    async with _sessionmaker_for_func() as session:
        total_place_top = await session.scalar(
            select(Value.value_int).where(Value.name == "TOTAL_PLACE_TOP")
        )
        users = await session.scalars(select(User))
        users = users.all()
        users_income = [(user, await income_(user)) for user in users]
        users_income.sort(key=lambda x: x[1], reverse=True)

        async def format_text(user, income, counter, unity_name):
            pattern = "pattern_line_top_self_place" if user.idpk == idpk_user else "pattern_line_top_user"
            return await get_text_message(
                pattern,
                n=user.nickname,
                i=income,
                c=counter,
                u=unity_name or '',
            )

        text = ""
        for counter, (user, income) in enumerate(users_income, start=1):
            unity = user.current_unity.split(':')[-1]
            unity = await session.get(Unity, unity)
            if counter > total_place_top:
                break
            text += await format_text(user, income, counter, unity.name if unity else '')

        self_place, user_data = next(
            (place, user_data) for place, user_data in enumerate(users_income, start=1)
            if user_data[0].idpk == idpk_user
        )
        if self_place > total_place_top:
            text += await get_text_message(
                "pattern_line_not_in_top",
                n=user_data[0].nickname,
                i=user_data[1],
                c=self_place,
            )
        return text

