from abc import ABC, abstractmethod


class NumberFormatter(ABC):
    """Абстрактный класс для форматирования чисел."""

    @abstractmethod
    def format_number(self, number: int) -> str:
        """Метод для форматирования числа."""
        pass


class SextillionFormatter(NumberFormatter):
    """Форматировщик для секстиллионов."""

    threshold = 1_000_000_000_000_000_000_000

    def format_number(self, number: int) -> str:
        return f"{number / 1_000_000_000_000_000_000_000:,.1f}Sx"


class QuintillionFormatter(NumberFormatter):

    threshold = 1_000_000_000_000_000_000

    def format_number(self, number: int) -> str:
        return f"{number / 1_000_000_000_000_000_000:,.1f}Qn"


class QuadrillionFormatter(NumberFormatter):

    threshold = 1_000_000_000_000_000

    def format_number(self, number: int) -> str:
        return f"{number / 1_000_000_000_000_000:,.1f}Qd"


class TrillionFormatter(NumberFormatter):
    """Форматировщик для триллионов."""

    threshold = 1_000_000_000_000

    def format_number(self, number: int) -> str:
        return f"{number / 1_000_000_000_000:,.1f}T"


class BillionFormatter(NumberFormatter):
    """Форматировщик для миллиардов."""

    threshold = 1_000_000_000

    def format_number(self, number: int) -> str:
        return f"{number / 1_000_000_000:,.1f}B"


class MillionFormatter(NumberFormatter):
    """Форматировщик для миллионов."""

    threshold = 1_000_000

    def format_number(self, number: int) -> str:
        return f"{number / 1_000_000:,.1f}M"


class ThousandFormatter(NumberFormatter):
    """Форматировщик для тысяч."""

    threshold = 1_000

    def format_number(self, number: int) -> str:
        return f"{number / 1_000:,.1f}k"


class DefaultFormatter(NumberFormatter):
    """Форматировщик по умолчанию для чисел меньше 1000."""

    threshold = 0

    def format_number(self, number: int) -> str:
        return f"{number:,.0f}"


class LargeNumberFormatter:
    """Класс для выбора подходящего форматировщика."""

    def __init__(self):
        self.formatters = [
            SextillionFormatter(),
            QuintillionFormatter(),
            QuadrillionFormatter(),
            TrillionFormatter(),
            BillionFormatter(),
            MillionFormatter(),
            ThousandFormatter(),
            DefaultFormatter(),
        ]

    def format_large_number(self, number: int | float, **kw) -> str:
        """Выбор форматировщика и форматирование числа."""
        for formatter in self.formatters:
            if number < formatter.threshold:
                continue
            return formatter.format_number(number)


# Примеры использования
formatter = LargeNumberFormatter()
