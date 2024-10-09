import datetime
import os
from pathlib import Path

import matplotlib.pyplot as plt
from db import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import tools


async def remove_file_plot(pattern: str):
    current_directory = Path(os.getcwd())
    # Проход по всем файлам в текущей директории, соответствующим шаблону
    for file_path in current_directory.glob(pattern):
        if file_path.is_file():
            file_path.unlink()


async def get_top_income_data(session: AsyncSession):
    r = await session.scalars(select(User).where(User.animals != "{}"))
    data = [(i.nickname, await tools.income_(session=session, user=i)) for i in r.all()]
    data.sort(key=lambda x: x[1], reverse=True)
    data = [i for c, i in enumerate(data) if c < 10]
    return data[::-1]


async def get_top_referrals_data(session: AsyncSession):
    r = await session.scalars(select(User).where(User.animals != "{}"))
    data = [
        (i.nickname, await tools.get_referrals(session=session, user=i))
        for i in r.all()
    ]
    data.sort(key=lambda x: x[1], reverse=True)
    data = [i for c, i in enumerate(data) if c < 10]
    return data[::-1]


async def get_top_animals_data(session: AsyncSession):
    r = await session.scalars(select(User).where(User.animals != "{}"))
    data = [(i.nickname, await tools.get_total_number_animals(self=i)) for i in r.all()]
    data.sort(key=lambda x: x[1], reverse=True)
    data = [i for c, i in enumerate(data) if c < 10]
    return data[::-1]


async def get_top_money_data(session: AsyncSession):
    r = await session.scalars(select(User).where(User.animals != "{}"))
    data = [(i.nickname, i.usd) for i in r.all()]
    data.sort(key=lambda x: x[1], reverse=True)
    data = [i for c, i in enumerate(data) if c < 10]
    return data[::-1]


async def gen_plot(
    nicks: list[str],
    values: list[int],
    color: str,
    xlabel: str,
    ylabel: str,
    type: str,
):
    plt.figure(figsize=(12, 5))
    bars = plt.barh(nicks, values, color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title("Топ")
    plt.grid(True, axis="x", linestyle="--", alpha=0.7)
    values = [float(value) for value in values]
    max_width = max(values)
    for bar in bars:
        width = bar.get_width()
        if width > 0:
            is_small_value = (max_width // (width)) > 7
            label_x_pos = 0.01 * max_width if is_small_value else width / 2
            alignment = "left" if is_small_value else "center"
            color = "black" if is_small_value else "white"
        else:
            label_x_pos = 0.01 * max_width
            alignment = "left"
            color = "black"
        plt.text(
            label_x_pos,
            bar.get_y() + bar.get_height() / 2,
            f"{width:,.0f}",
            ha=alignment,
            va="center",
            color=color,
        )
    now_time = datetime.datetime.now().strftime("%m_%d_%H_%M")
    name = f"plot_{type}_{now_time}.png"
    if not os.path.exists(name):
        await remove_file_plot(pattern=f"plot_{type}_*.png")
        plt.savefig(name, dpi=300, bbox_inches="tight")
        plt.close("all")
    return name


async def get_plot(session: AsyncSession, type: str):
    config = {
        "income": ("royalblue", "Доход", "Игроки", get_top_income_data),
        "referrals": (
            "mediumpurple",
            "Рефералы",
            "Игроки",
            get_top_referrals_data,
        ),
        "animals": ("indianred", "Животные", "Игроки", get_top_animals_data),
        "money": ("darkgreen", "Доллары", "Игроки", get_top_money_data),
    }

    if type in config:
        color, xlabel, ylabel, data_func = config[type]
        data = await data_func(session)
        if not data:
            return None
        nicks, values = zip(*data)
        return await gen_plot(
            nicks=nicks,
            values=values,
            color=color,
            xlabel=xlabel,
            ylabel=ylabel,
            type=type,
        )
