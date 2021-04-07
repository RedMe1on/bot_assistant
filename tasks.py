"""Работа с задачами"""
import re
from typing import Dict, List, NamedTuple, Any
from datetime import date, datetime, timedelta
import db
import exceptions
from mixins import ObjectMixin


class Task(NamedTuple):
    """Структура задач"""
    description: str
    date_: str


class Message(NamedTuple):
    """Структура распаршенного сообщения о новой задаче"""
    date: str
    description: str


class Tasks(ObjectMixin):
    table = "tasks"
    column_string = "id description date_"

    def get_date_without_deadline(self):
        """Возвращает задачи без срока"""
        data_tasks = []
        for task in self._all_objects:
            if task.get('date_') is None:
                data_tasks.append(task)
        return data_tasks

    def get_tasks_with_days_interval(self, number_of_days: int) -> List[dict]:
        """Возвращает задачи за определенный период"""
        data_tasks = []
        date_task = (datetime.now() + timedelta(days=number_of_days)).date()
        if number_of_days == 0 or number_of_days == 1:
            for task in self._all_objects:
                if task.get('date_'):
                    date_ = datetime.strptime(task.get('date_'), "%d/%m/%y").date()
                    if date_ == date_task:
                        data_tasks.append(task)
        elif number_of_days > 1:
            for task in self._all_objects:
                if task.get('date_'):
                    date_ = datetime.strptime(task.get('date_'), "%d/%m/%y").date()
                    if date_ <= date_task and (date_task - date_).days <= number_of_days:
                        data_tasks.append(task)
        return data_tasks

    def get_overdue_tasks(self) -> List[dict]:
        """Возвращает просроченные задачи"""
        data_tasks = []
        for task in self._all_objects:
            if task.get('date_'):
                date_ = datetime.strptime(task.get('date_'), "%d/%m/%y").date()
                if date_ < datetime.now().date():
                    data_tasks.append(task)
        return data_tasks

    @classmethod
    def delete_task(cls, row_id: int):
        """Удаляет задачу по ее id"""
        db.delete(cls.table, row_id)

    @classmethod
    def add_task(cls, raw_message: str) -> Task:
        """Добавляет новую задачу
        Принимает на вход текст сообщения, пришедшего в бот"""
        # разделяет строку столбцов на три, две из которых мы используем в словаре
        column_names = cls.column_string.split()
        parsed_message = Tasks._parse_message(raw_message)
        inserted_row_id = db.insert(cls.table, {
            column_names[1]: parsed_message.description,
            column_names[2]: parsed_message.date,
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
