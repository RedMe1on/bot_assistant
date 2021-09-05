import os
from typing import Dict, List

import sqlite3

import exceptions

conn = sqlite3.connect(os.path.join("db", "task_assistant.db"))
cursor = conn.cursor()


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def update(table: str, column_dict: Dict, row_id: int) -> None:
    set_value = [f'{str(column)} = ?' for column in column_dict]
    set_value = ', '.join(set_value)
    values = tuple(column_dict.values())
    cursor.execute(f"UPDATE {table} SET {set_value} WHERE id = {row_id}", values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Dict]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def fetchone(table: str, columns: List[str], row_id: int) -> Dict:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table} WHERE id={row_id}")
    result = cursor.fetchone()
    if result is None:
        raise exceptions.ObjectDoesNotExist('Фак! Объекта не существует в моей памяти')
    dict_result = {}
    for index, column in enumerate(columns):
        dict_result[column] = result[index]
    return dict_result


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id={row_id}")
    conn.commit()


def get_cursor():
    return cursor


def _init_db():
    """Инициализирует БД"""
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='tasks'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


def db_update_stoicism_quotes():
    """Запускает скрипт с обновлением базы данных"""
    with open("add_stoicism_quotes.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_update_stoicism():
    """Проверяет, обновлена ли база данных фразами стоицизма, если нет — добавляет"""
    cursor.execute("SELECT text FROM stoicism_quote")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    db_update_stoicism_quotes()


check_db_exists()
check_db_update_stoicism()
