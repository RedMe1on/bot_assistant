import json

from aiogram.dispatcher.filters.state import State, StatesGroup

import exceptions
from tasks import Tasks


class StateAddTask(StatesGroup):
    """Состояния при добавлении задачи"""
    add = State()


class StateSetMorningTime(StatesGroup):
    """Машина состояний для настройки утреннего времени"""
    set = State()


class StateUpdateTask(StatesGroup):
    """Машина состояний для обновления задачи"""
    full = State()
    date = State()
    description = State()


def send_today_tasks_message() -> str:
    """Возвращает результирующую строку при отправке задач на сегодня
    т.к. хендлер ожидает сообщения, чтобы его не эмулировать создана эта функция, чтобы следовать принципу DRY"""
    today_tasks = Tasks().get_tasks_with_days_interval(0)
    if len(today_tasks) != 0:
        result_string = 'Сегодня у тебя много работы, прям завал:\n'
        for index, task in enumerate(today_tasks):
            result_string += f'\n<b>{index + 1}.</b> {task.get("description")}\n' \
                             f'\nУдалить: /del{task.get("id")}\n' \
                             f'Обновить: /update{task.get("id")}\n'
    else:
        result_string = 'Ты сегодня самый занятой человек планеты, у тебя целых 0 задач на сегодня!\n' \
                        'Лучше попроси парочку из полного списка или добавь себе работы!'
    return result_string


def validate_morning_time(message: str) -> int:
    """Валидация сообщения при изменении утреннего времени"""
    msg_error = 'Нужно только число от 0 до 23!'
    try:
        morning_hour = int(message)
        if not 0 <= morning_hour <= 23:
            raise exceptions.NotCorrectMessage(msg_error)
    except ValueError:
        raise exceptions.NotCorrectMessage(msg_error)
    return morning_hour


def load_config() -> dict:
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config


def change_config(config: dict) -> None:
    with open('config.json', 'w') as f:
        json.dump(config, f)
