from sqlalchemy import select
from db import Text, Button, Value
from init_db import _sessionmaker_for_func


async def get_text_message(name: str, **kw) -> str:
    async with _sessionmaker_for_func() as session:
        text_obj: Text = await session.scalar(select(Text).where(Text.name == name))
        if not text_obj:
            session.add(Text(name=name))
            await session.commit()
            return f'[{name}]\nтекст не задан'
        debug_text = await session.scalar(select(Value.value_int).where(Value.name == 'debug_text'))
        match debug_text:
            case 0:
                return text_obj.text.format(**kw) if kw else text_obj.text
            case 1:
                return f'[{text_obj.name}]\n{text_obj.text.format(**kw)}' if kw else f'[{text_obj.name}]\n{text_obj.text}'


async def get_text_button(name: str, **kw) -> str:
    async with _sessionmaker_for_func() as session:
        bttn_obj: Text = await session.scalar(select(Button).where(Button.name == name))
        if not bttn_obj:
            session.add(Button(name=name))
            await session.commit()
            return f'[{name}]\nкнопка'
        debug_button = await session.scalar(select(Value.value_int).where(Value.name == 'debug_button'))
        match debug_button:
            case 0:
                return bttn_obj.text.format(**kw) if kw else bttn_obj.text
            case 1:
                return f'[{bttn_obj.name}]\n{bttn_obj.text.format(**kw)}' if kw else f'[{bttn_obj.name}]\n{bttn_obj.text}'


def mention_html(id_user: int, name: str) -> str:
    return f'<a href="tg://user?id={id_user}">{name}</a>'