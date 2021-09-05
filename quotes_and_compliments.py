from typing import NamedTuple
from mixins import ObjectMixin


class Quote(NamedTuple):
    """Структура цитаты"""
    text: str
    author: str


class StoicismQuote(NamedTuple):
    """Структура цитаты"""
    text: str
    author: str


class Compliment(NamedTuple):
    """Структура комплимента"""
    text: str


class Quotes(ObjectMixin):
    """Класс для работы с цитатами"""
    table = 'quotes'
    column_string = "id text author"


class StoicismQuotes(ObjectMixin):
    """Класс для работы с цитатами стоицизма"""
    table = 'stoicism_quote'
    column_string = "id text author"


class Compliments(ObjectMixin):
    """Класс для работы с комплиментами"""
    table = 'compliments'
    column_string = "id text"
