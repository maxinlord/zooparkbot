
from aiogram.filters import Filter
from aiogram.types import Message
from tools import get_text_button


class GetTextButton(Filter):
    def __init__(self, name: str) -> None:
        self.name = name

    async def __call__(self, message: Message) -> bool:
        return message.text == await get_text_button(self.name)
    