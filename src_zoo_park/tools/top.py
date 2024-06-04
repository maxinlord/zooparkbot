from sqlalchemy import select
from db import Text, Button, Value, User
from init_db import _sessionmaker_for_func
from tools import income, get_text_message


async def factory_text_main_top(idpk_user: int) -> str:
    async with _sessionmaker_for_func() as session:
        total_place_top = 10
        users = await session.scalars(select(User))
        users = users.all()
        users_income = [await income(user) for user in users]
        ls = list(zip(users, users_income))
        ls.sort(key=lambda x: x[1], reverse=True)
        # формирование текста
        text = ""
        for counter, (user, i) in enumerate(ls, start=1):
            if counter > total_place_top:
                break
            if user.idpk == idpk_user:
                text += await get_text_message(
                    "pattern_line_top_self_place",
                    n=user.nickname,
                    i=i,
                    c=counter,
                )
                continue
            text += await get_text_message(
                "pattern_line_top_user",
                n=user.nickname,
                i=i,
                c=counter,
            )
        # получение собственного места в топе
        self_place, user_data = [
            [place, user_data]
            for place, user_data in enumerate(ls, start=1)
            if user_data[0].idpk == idpk_user
        ][0]
        if self_place > total_place_top:
            text += await get_text_message(
                "pattern_line_not_in_top",
                n=user_data[0].nickname,
                i=user_data[1],
                c=self_place,
            )
        return text
