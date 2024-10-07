import json

import ahocorasick
from cache import button_cache, text_cache
from db import Animal, Aviary, Button, Game, Gamer, Text, Unity, User, Value
from init_db import _sessionmaker_for_func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import tools


async def get_text_message(name: str, **kw) -> str:
    async with _sessionmaker_for_func() as session:
        if name in text_cache:
            text_obj = text_cache[name]
        else:
            text_obj = await _get_or_create_text(session, name)
            text_cache[name] = text_obj

        debug_key = "debug_key_text"
        if debug_key in text_cache:
            debug_text = text_cache[debug_key]
        else:
            debug_text = await session.scalar(
                select(Value.value_int).where(Value.name == "DEBUG_TEXT")
            )
            text_cache[debug_key] = debug_text
        formatted_text = await _format_text(
            text_obj=text_obj,
            debug_text=debug_text,
            kw=kw,
        )
        await session.commit()
        return formatted_text


async def _get_or_create_text(session: AsyncSession, name: str):
    text_obj = await session.scalar(select(Text).where(Text.name == name))
    if not text_obj:
        text_obj = Text(name=name)
        session.add(text_obj)
        await session.commit()
    return text_obj


async def _get_or_create_button(session, name):
    bttn_obj: Text = await session.scalar(select(Button).where(Button.name == name))
    if not bttn_obj:
        bttn_obj = Button(name=name)
        session.add(bttn_obj)
    return bttn_obj


async def _format_text(text_obj: Text, kw: dict, debug_text: int = 0):
    prefix = f"[{text_obj.name}]\n" if debug_text else ""
    if not kw:
        return f"{prefix}{text_obj.text}"
    for k, v in kw.items():
        if k not in text_obj.text:
            key = f"{{{k}:,d}}" if str(v).isdigit() else f"{{{k}}}"
            text_obj.text += f"\n{k}: {key}"
    return f"{prefix}{text_obj.text.format(**kw)}"


async def _format_button(bttn_obj: Text, kw: dict, debug_button: int = 0):
    prefix = f"[{bttn_obj.name}]|" if debug_button else ""
    if not kw:
        return f"{prefix}{bttn_obj.text}"
    for k, v in kw.items():
        if k not in bttn_obj.text:
            key = f"{{{k}:,d}}" if str(v).isdigit() else f"{{{k}}}"
            bttn_obj.text += f"|{key}"
    return f"{prefix}{bttn_obj.text.format(**kw)}"


async def get_text_button(name: str, **kw) -> str:
    async with _sessionmaker_for_func() as session:
        if name in button_cache:
            bttn_obj = button_cache[name]
        else:
            bttn_obj = await _get_or_create_button(session, name)
            button_cache[name] = bttn_obj

        debug_key = "debug_key_button"
        if debug_key in button_cache:
            debug_button = button_cache[debug_key]
        else:
            debug_button = await session.scalar(
                select(Value.value_int).where(Value.name == "DEBUG_BUTTON")
            )
            button_cache[debug_key] = debug_button
        formatted_bttn = await _format_button(
            bttn_obj=bttn_obj,
            kw=kw,
            debug_button=debug_button,
        )
        await session.commit()
        return formatted_bttn


def mention_html(id_user: int, name: str) -> str:
    return f'<a href="tg://user?id={id_user}">{name}</a>'


def mention_html_by_username(username: str, name: str) -> str:
    return f'<a href="http://t.me/{username}">{name}</a>' if username else name


async def factory_text_unity_top(session: AsyncSession) -> str:
    unites = await session.scalars(select(Unity))
    unites = unites.all()
    unites_income = [
        await tools.count_income_unity(session=session, unity=unity) for unity in unites
    ]
    ls = list(zip(unites, unites_income))
    ls.sort(key=lambda x: x[1], reverse=True)
    text = ""
    for counter, ls_obj in enumerate(ls, start=1):
        unity = ls_obj[0]
        i = tools.formatter.format_large_number(ls_obj[1])
        text += (
            await tools.get_text_message(
                "pattern_line_top_unity",
                n=unity.format_name,
                i=i,
                c=counter,
                lvl=unity.level,
            )
            + "\n"
        )
    return text


async def factory_text_main_top(session: AsyncSession, idpk_user: int) -> str:
    total_place_top = await tools.get_value(
        session=session, value_name="TOTAL_PLACE_TOP"
    )
    users = await tools.fetch_users_for_top(session=session, idpk_user=idpk_user)
    if not users:
        return await get_text_message("top_not_exist")
    users_and_incomes = [
        (user, await tools.income_(session=session, user=user)) for user in users
    ]

    def func_sort_by_income(x):
        return x[1]

    users_and_incomes.sort(key=func_sort_by_income, reverse=True)

    async def format_text(user, income, counter, unity_name):
        pattern = (
            "pattern_line_top_self_place"
            if user.idpk == idpk_user
            else "pattern_line_top_user"
        )
        return await tools.get_text_message(
            pattern,
            n=await tools.view_nickname(session=session, user=user),
            i=tools.formatter.format_large_number(income),
            c=counter,
            u=unity_name,
        )

    text = ""
    for counter, (user, income) in enumerate(users_and_incomes, start=1):
        if counter > total_place_top:
            break
        unity_idpk = tools.get_unity_idpk(user.current_unity)
        unity = await tools.fetch_unity(session=session, idpk_unity=unity_idpk)
        text += await format_text(user, income, counter, unity.format_name)
    self_place, user_data = next(
        (place, user_data)
        for place, user_data in enumerate(users_and_incomes, start=1)
        if user_data[0].idpk == idpk_user
    )
    if self_place > total_place_top:
        text += await tools.get_text_message(
            "pattern_line_not_in_top",
            n=user_data[0].nickname,
            i=user_data[1],
            c=self_place,
        )
    return text


async def factory_text_main_top_by_money(session: AsyncSession, idpk_user: int) -> str:
    total_place_top = await tools.get_value(
        session=session, value_name="TOTAL_PLACE_TOP"
    )
    users = await tools.fetch_users_for_top(session=session, idpk_user=idpk_user)
    if not users:
        return await get_text_message("top_not_exist")
    users.sort(key=lambda x: x.usd, reverse=True)

    async def format_text(user, money, counter, unity_name):
        pattern = (
            "pattern_line_top_self_place_money"
            if user.idpk == idpk_user
            else "pattern_line_top_user_money"
        )
        return await tools.get_text_message(
            pattern,
            n=await tools.view_nickname(session=session, user=user),
            m=tools.formatter.format_large_number(money),
            c=counter,
            u=unity_name,
        )

    text = ""
    for counter, user in enumerate(users, start=1):
        if counter > total_place_top:
            break
        unity_idpk = tools.get_unity_idpk(user.current_unity)
        unity = await tools.fetch_unity(session=session, idpk_unity=unity_idpk)
        text += await format_text(user, user.usd, counter, unity.format_name)

    self_place, user = next(
        (place, user)
        for place, user in enumerate(users, start=1)
        if user.idpk == idpk_user
    )
    if self_place > total_place_top:
        text += await tools.get_text_message(
            "pattern_line_not_in_top_money",
            n=await tools.view_nickname(session=session, user=user),
            m=user.usd,
            c=self_place,
        )
    return text


async def factory_text_main_top_by_animals(
    session: AsyncSession, idpk_user: int
) -> str:
    total_place_top = await tools.get_value(
        session=session, value_name="TOTAL_PLACE_TOP"
    )
    users = await tools.fetch_users_for_top(session=session, idpk_user=idpk_user)
    if not users:
        return await get_text_message("top_not_exist")
    users_animals = [
        (user, await tools.get_total_number_animals(self=user)) for user in users
    ]
    users_animals.sort(key=lambda x: x[1], reverse=True)

    async def format_text(user, animals, counter, unity_name):
        pattern = (
            "pattern_line_top_self_place_animals"
            if user.idpk == idpk_user
            else "pattern_line_top_user_animals"
        )
        return await tools.get_text_message(
            pattern,
            n=await tools.view_nickname(session=session, user=user),
            a=animals,
            c=counter,
            u=unity_name,
        )

    text = ""
    for counter, (user, animals) in enumerate(users_animals, start=1):
        if counter > total_place_top:
            break
        unity_idpk = tools.get_unity_idpk(user.current_unity)
        unity = await tools.fetch_unity(session=session, idpk_unity=unity_idpk)
        text += await format_text(user, animals, counter, unity.format_name)

    self_place, user_data = next(
        (place, user_data)
        for place, user_data in enumerate(users_animals, start=1)
        if user_data[0].idpk == idpk_user
    )
    if self_place > total_place_top:
        text += await tools.get_text_message(
            "pattern_line_not_in_top_animals",
            n=user_data[0].nickname,
            a=user_data[1],
            c=self_place,
        )
    return text


async def factory_text_main_top_by_referrals(
    session: AsyncSession, idpk_user: int
) -> str:
    total_place_top = await tools.get_value(
        session=session, value_name="TOTAL_PLACE_TOP"
    )
    users = await tools.fetch_users_for_top(session=session, idpk_user=idpk_user)
    if not users:
        return await get_text_message("top_not_exist")
    users_referrals = [
        (user, await tools.get_referrals(session=session, user=user)) for user in users
    ]
    users_referrals.sort(key=lambda x: x[1], reverse=True)

    async def format_text(user, ref, counter, unity_name):
        pattern = (
            "pattern_line_top_self_place_referrals"
            if user.idpk == idpk_user
            else "pattern_line_top_user_referrals"
        )
        return await tools.get_text_message(
            pattern,
            n=await tools.view_nickname(session=session, user=user),
            r=ref,
            c=counter,
            u=unity_name,
        )

    text = ""
    for counter, (user, ref) in enumerate(users_referrals, start=1):
        if counter > total_place_top:
            break
        unity_idpk = tools.get_unity_idpk(user.current_unity)
        unity = await tools.fetch_unity(session=session, idpk_unity=unity_idpk)
        text += await format_text(user, ref, counter, unity.format_name)

    self_place, user_data = next(
        (place, user_data)
        for place, user_data in enumerate(users_referrals, start=1)
        if user_data[0].idpk == idpk_user
    )
    if self_place > total_place_top:
        text += await tools.get_text_message(
            "pattern_line_not_in_top_referrals",
            n=user_data[0].nickname,
            r=user_data[1],
            c=self_place,
        )
    return text


async def factory_text_top_mini_game(session: AsyncSession, game: Game):
    gamers = await session.scalars(select(Gamer).where(Gamer.id_game == game.id_game))
    gamers = list(gamers)
    gamers_sorted = sorted(gamers, key=lambda x: x.score, reverse=True)
    text = ""
    for counter, gamer in enumerate(gamers_sorted, start=1):
        user = await session.get(User, gamer.idpk_gamer)
        nickname = (
            mention_html_by_username(
                username=user.username,
                name=await tools.view_nickname(session=session, user=user),
            )
            if user.nickname
            else user.nickname
        )
        text += await get_text_message(
            "pattern_place_in_top_game",
            name_=nickname,
            score=gamer.score,
            c=counter,
            m=gamer.moves,
        )
    return text


async def factory_text_account_animals(session: AsyncSession, animals: str) -> str:
    text = ""
    animals = json.loads(animals)
    sorted_keys = sorted(animals, key=lambda x: animals[x], reverse=True)
    for animal in sorted_keys:
        name = await session.scalar(
            select(Animal.name).where(Animal.code_name == animal)
        )
        text += await get_text_message(
            "pattern_account_animals",
            name_=name,
            amount=animals[animal],
        )
    return text


async def factory_text_account_aviaries(session: AsyncSession, aviaries: str) -> str:
    text = ""
    aviaries = json.loads(aviaries)
    sorted_keys = sorted(aviaries, key=lambda x: aviaries[x]["quantity"], reverse=True)
    for aviary in sorted_keys:
        name = await session.scalar(
            select(Aviary.name).where(Aviary.code_name == aviary)
        )
        text += await get_text_message(
            "pattern_account_aviaries",
            name_=name,
            quantity=aviaries[aviary]["quantity"],
        )
    return text


async def ft_bank_exchange_info(
    you_change: int,
    you_got: int,
    rate: int,
    bank_got: int = None,
    referrer_got: int = None,
):  # ft - factory text
    t_bank_got = ""
    t_referrer_got = ""
    t_rate = await get_text_message("pattern_bank_rate", rate=rate)
    t_you_change = await get_text_message(
        "pattern_bank_you_change", you_change=you_change
    )
    if bank_got:
        t_bank_got = await get_text_message("pattern_bank_bank_got", bank_got=bank_got)
    if referrer_got:
        t_referrer_got = await get_text_message(
            "pattern_bank_referrer_got", referrer_got=referrer_got
        )

    t_you_got = await get_text_message("pattern_bank_you_got", you_got=you_got)
    text = await get_text_message(
        "pattern_bank_exchange_info",
        t_rate=t_rate,
        t_you_change=t_you_change,
        t_bank_got=t_bank_got or f"{t_bank_got}\n",
        t_referrer_got=t_referrer_got or f"{t_referrer_got}\n",
        t_you_got=t_you_got,
    )
    return text


async def ft_bonus_info(
    data_bonus: tools.DataBonus,
):
    text = ""
    match data_bonus.bonus_type:
        case "rub":
            text = await get_text_message("bonus_rub", rub=data_bonus.result_func)
        case "usd":
            text = await get_text_message("bonus_usd", usd=data_bonus.result_func)
        case "aviary":
            text = await get_text_message(
                "bonus_aviary",
                aviary=data_bonus.result_func[0]["name"],
                amount=data_bonus.result_func[1],
            )
        case "animal":
            text = await get_text_message(
                "bonus_animal",
                animal=data_bonus.result_func[0]["name"],
                amount=data_bonus.result_func[1],
            )
        case "item":
            text = await get_text_message(
                "bonus_item", item=data_bonus.result_func["name_with_emoji"]
            )
        case "paw_coins":
            text = await get_text_message(
                "bonus_paw_coin",
                amount=data_bonus.result_func,
            )
    text = await get_text_message(
        "bonus_received",
        text=text,
    )
    return text


async def ft_item_props(item_props: dict | str):
    if isinstance(item_props, str):
        item_props = json.loads(item_props)
    t = []
    item_props = sorted(item_props.items(), key=lambda x: x[1], reverse=True)
    for k, v in item_props:
        name_prop = await get_text_message(name=k)
        value = await get_text_message(name=f"{k}_value_pattern", v=v)
        pattern_item_prop_line = await get_text_message(
            "pattern_item_prop_line", name_prop=name_prop, v=value
        )
        t.append(pattern_item_prop_line)
    return "".join(t)


async def ft_item_props_for_update(
    item_props: dict | str, updated_prop: str, parameter: int
):
    if isinstance(item_props, str):
        item_props = json.loads(item_props)
    t = []
    for k, v in item_props.items():
        name_prop = await get_text_message(name=k)
        value = await get_text_message(name=f"{k}_value_pattern", v=v)
        if k == updated_prop:
            pattern = await get_text_message(
                "pattern_item_prop_for_update_line",
                name_prop=name_prop,
                v=value,
                parameter=parameter,
            )
        else:
            pattern = await get_text_message(
                "pattern_item_prop_line", name_prop=name_prop, v=value
            )
        t.append(pattern)
    return "".join(t)


def contains_any_pattern(text, patterns):

    if not isinstance(text, str):
        return False

    # Создаем автомат
    A = ahocorasick.Automaton()

    # Добавляем все шаблоны в автомат
    for idx, pattern in enumerate(patterns):
        A.add_word(pattern, (idx, pattern))

    # Строим автомат
    A.make_automaton()

    # Поиск вхождений, если хотя бы одно найдено, возвращаем True
    for end_idx, (idx, pattern) in A.iter(text):
        return True  # Нашли хотя бы одно вхождение

    return False  # Ничего не нашли
