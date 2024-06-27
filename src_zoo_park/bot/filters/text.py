from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery, InlineQuery
from tools import get_text_button, find_integers


class GetTextButton(Filter):
    def __init__(self, name: str) -> None:
        self.name = name

    async def __call__(self, message: Message) -> bool:
        return message.text == await get_text_button(self.name)


class CompareDataByIndex(Filter):
    def __init__(self, compare: str, index: int = -1, sep: str = ":") -> None:
        self.compare = compare
        self.index = index
        self.sep = sep

    async def __call__(
        self,
        query: CallbackQuery,
    ) -> bool:
        return query.data.split(self.sep)[self.index] == self.compare


class FindIntegers(Filter):

    async def __call__(self, inline_query: InlineQuery) -> bool:
        try:
            return bool(await find_integers(inline_query.query.split()[0]))
        except Exception:
            return False
