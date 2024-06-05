from sqlalchemy import select
from db import Text, Button, Value
from init_db import _sessionmaker_for_func


async def get_text_message(name: str, **kw) -> str:
    async with _sessionmaker_for_func() as session:
        text_obj: Text = await session.scalar(select(Text).where(Text.name == name))
        if not text_obj:
            text_obj = Text(name=name)
            session.add(text_obj)
            await session.commit()
        debug_text = await session.scalar(
            select(Value.value_int).where(Value.name == "DEBUG_TEXT")
        )
        match debug_text:
            case 0:
                if not kw:
                    return text_obj.text
                for k, v in kw.items():
                    if k not in text_obj.text:
                        key = f"{{{k}:,d}}" if str(v).isdigit() else f"{{{k}}}"
                        text_obj.text += f"\n{k}: {key}"
                await session.commit()
                return text_obj.text.format(**kw)
            case 1:
                if not kw:
                    return f"[{text_obj.name}]\n{text_obj.text}"
                for k, v in kw.items():
                    if k not in text_obj.text:
                        key = f"{{{k}:,d}}" if str(v).isdigit() else f"{{{k}}}"
                        text_obj.text += f"\n{k}: {key}"
                await session.commit()
                return f"[{text_obj.name}]\n{text_obj.text.format(**kw)}"


async def get_text_button(name: str, **kw) -> str:
    async with _sessionmaker_for_func() as session:
        bttn_obj: Text = await session.scalar(select(Button).where(Button.name == name))
        if not bttn_obj:
            text = "|".join([f"{{{i}}}" for i in kw])
            session.add(Button(name=name))
            await session.commit()
            return f"[{name}] - {text}"
        debug_button = await session.scalar(
            select(Value.value_int).where(Value.name == "DEBUG_BUTTON")
        )
        match debug_button:
            case 0:
                if not kw:
                    return bttn_obj.text
                for i in kw:
                    if i not in bttn_obj.text:
                        bttn_obj.text += f"|{{{i}}}"
                await session.commit()
                return bttn_obj.text.format(**kw)
            case 1:
                if not kw:
                    return f"[{bttn_obj.name}] - {bttn_obj.text}"
                for i in kw:
                    if i not in bttn_obj.text:
                        bttn_obj.text += f"|{{{i}}}"
                await session.commit()
                return f"[{bttn_obj.name}] - {bttn_obj.text.format(**kw)}"


def mention_html(id_user: int, name: str) -> str:
    return f'<a href="tg://user?id={id_user}">{name}</a>'
