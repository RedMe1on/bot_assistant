import random
from typing import List

import db


class ObjectMixin:
    """Миксин для загрузки всех объектов и рандомного объекта"""
    table = None
    column_string = None

    def __init__(self):
        self._load_all_objects()

    def _load_all_objects(self):
        """Возвращает справочник объектов из БД"""
        self._all_objects = db.fetchall(
            self.table, self.column_string.split()
        )

    def get_all_objects(self) -> List[dict]:
        """Возвращает справочник объектов."""
        return self._all_objects

    def get_random_object(self) -> dict:
        """Возвращает случайный объект"""
        return random.choice(self._all_objects)
