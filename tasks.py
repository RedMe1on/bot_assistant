"""Работа с задачами"""
import random
import re
from typing import Dict, List, NamedTuple, Any
from datetime import date, datetime, timedelta
import db
import exceptions


class Task(NamedTuple):
    """Структура задач"""
    description: str
    date_: str


class Message(NamedTuple):
    """Структура распаршенного сообщения о новой задаче"""
    date: str
    description: str


class Tasks:
    def __init__(self):
        self._tasks = None
        self._load_tasks()

    def _load_tasks(self):
        """Возвращает справочник задач из БД"""
        self._tasks = db.fetchall(
            "tasks", "id description date_".split()
        )

    def get_all_tasks(self) -> List[dict]:
        """Возвращает справочник задач."""
        return self._tasks

    def get_random_task(self) -> dict:
        """Возвращает случайную задачу"""
        return random.choice(self._tasks)

    def get_tasks_with_days_interval(self, number_of_days: int) -> List[dict]:
        """Возвращает задачи за определенный период"""
        data_tasks = []
        date_task = datetime.now() + timedelta(days=number_of_days)
        for task in self._tasks:
            if task.get('date_') == date_task.strftime("%d/%m/%y"):
                data_tasks.append(task)
        return data_tasks

    def get_overdue_tasks(self) -> List[dict]:
        """Возвращает просроченные задачи"""
        data_tasks = []
        for task in self._tasks:
            if task.get('date_') < datetime.now().strftime("%d/%m/%y"):
                data_tasks.append(task)
        return data_tasks

    @staticmethod
    def delete_task(row_id: int):
        db.delete('tasks', row_id)

    @staticmethod
    def add_task(raw_message: str) -> Task:
        """Добавляет новую задачу
        Принимает на вход текст сообщения, пришедшего в бот"""
        parsed_message = Tasks._parse_message(raw_message)
        inserted_row_id = db.insert("tasks", {
            "description": parsed_message.description,
            "date_": parsed_message.date,
        })
        return Task(description=parsed_message.description, date_=parsed_message.date)

    @staticmethod
    def _parse_message(raw_message: str) -> Message:
        """Парсит текст пришедшего сообщения о новой задаче."""
        regexp_result = re.match(r"(\d{,2}[./-]\d{,2}[./-]?\d{0,4}) (.*)", raw_message.strip())
        if not regexp_result:
            task_date = None
            task_text = raw_message.strip()
        else:
            if not regexp_result.group(0) \
                    or not regexp_result.group(1) or not regexp_result.group(2):
                raise exceptions.NotCorrectMessage(
                    "Не могу понять сообщение.\n "
                    "Пиши в нужном формате без даты или с ней. \n"
                    "Дату в формате dd.mm.yy - можно использовать разделители, но только один тип: './-', "
                    "например:\n12.12.2020 Классная задача по гачимучи"
                    "\nКлассная задача по гачимучи"
                    "\n12.2.21 Классная задача по гачимучи")
            task_date = Tasks._format_date_with_validate(regexp_result.group(1))
            task_text = regexp_result.group(2).strip()
        return Message(date=task_date, description=task_text)

    @staticmethod
    def _format_date_with_validate(date_task: str) -> str:
        """Приведение даты к общему формату для записи в БД"""
        split_date = Tasks.split_date(date_task)
        try:
            day, mouth, year = split_date[0], split_date[1], split_date[2]
        except IndexError:
            day, mouth = split_date[0], split_date[1]
            year = str(datetime.now().year)
        try:
            if len(year) == 2:
                date_task = datetime.strptime(f"{int(day)}/{int(mouth)}/{int(year)}", "%d/%m/%y").strftime("%d/%m/%y")
            else:
                date_task = date(int(year), int(mouth), int(day)).strftime("%d/%m/%y")
        except ValueError:
            raise exceptions.NotCorrectData('Некоректная дата. Укажите существующую дату.\n'
                                            'Месяцев может быть только 12, а дней столько, сколько в указаном месяце')
        return date_task

    @staticmethod
    def split_date(date_task):
        """Разделяет дату по одному из трех доступных разделителей"""
        if len(date_task.split('/')) != 1:
            split_date = date_task.split('/')
        elif len(date_task.split('.')) != 1:
            split_date = date_task.split('.')
        elif len(date_task.split('-')) != 1:
            split_date = date_task.split('-')
        else:
            raise exceptions.NotCorrectData('Некоректная дата. Введите дату в формате dd.mm.yy\n'
                                            'Можно использовать разделители, но только один тип: "./-" ')
        return split_date
