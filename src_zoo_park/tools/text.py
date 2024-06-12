from sqlalchemy import select
from db import Text, Button, Value, Unity, User
from init_db import _sessionmaker_for_func
from cache import text_cache, button_cache


async def get_text_message(name: str, **kw) -> str:
    async with _sessionmaker_for_func() as session:
        if name in text_cache:
            text_obj = text_cache[name]
        else:
            text_obj = await get_or_create_text(session, name)
            text_cache[name] = text_obj

        debug_key = "debug_key_text"
        if debug_key in text_cache:
            debug_text = text_cache[debug_key]
        else:
            debug_text = await session.scalar(
                select(Value.value_int).where(Value.name == "DEBUG_TEXT")
            )
            text_cache[debug_key] = debug_text
        formatted_text = await format_text(
            text_obj=text_obj,
            debug_text=debug_text,
            kw=kw,
        )
        await session.commit()
        return formatted_text


async def get_or_create_text(session, name):
    text_obj = await session.scalar(select(Text).where(Text.name == name))
    if not text_obj:
        text_obj = Text(name=name)
        session.add(text_obj)
    return text_obj


async def get_or_create_button(session, name):
    bttn_obj: Text = await session.scalar(select(Button).where(Button.name == name))
    if not bttn_obj:
        bttn_obj = Button(name=name)
        session.add(bttn_obj)
    return bttn_obj


async def format_text(text_obj: Text, kw: dict, debug_text: int = 0):
    prefix = f"[{text_obj.name}]\n" if debug_text else ""
    if not kw:
        return f"{prefix}{text_obj.text}"
    for k, v in kw.items():
        if k not in text_obj.text:
            key = f"{{{k}:,d}}" if str(v).isdigit() else f"{{{k}}}"
            text_obj.text += f"\n{k}: {key}"
    return f"{prefix}{text_obj.text.format(**kw)}"


async def format_button(bttn_obj: Text, kw: dict, debug_button: int = 0):
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
            bttn_obj = await get_or_create_button(session, name)
            button_cache[name] = bttn_obj
        
        debug_key = "debug_key_button"
        if debug_key in button_cache:
            debug_button = button_cache[debug_key]
        else:
            debug_button = await session.scalar(
                select(Value.value_int).where(Value.name == "DEBUG_BUTTON")
            )
            button_cache[debug_key] = debug_button
        formatted_bttn = await format_button(
            bttn_obj=bttn_obj,
            kw=kw,
            debug_button=debug_button,
        )
        await session.commit()
        return formatted_bttn


def mention_html(id_user: int, name: str) -> str:
    return f'<a href="tg://user?id={id_user}">{name}</a>'


def mention_html_by_username(username: str, name: str) -> str:
    return f'<a href="http://t.me/{username}">{name}</a>'
