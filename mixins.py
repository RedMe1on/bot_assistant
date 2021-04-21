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

    def get_one_objects_by_id(self, row_id: int) -> dict:
        """Возвращает объект по id"""
        obj = db.fetchone(self.table, self.column_string.split(), row_id)
        return obj

    def get_all_objects(self) -> List[dict]:
        """Возвращает справочник объектов."""
        return self._all_objects

    def get_random_object(self) -> dict or None:
        """Возвращает случайный объект"""
        if self._all_objects:
            return random.choice(self._all_objects)
        else:
            return None
