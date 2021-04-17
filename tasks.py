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
    description: str or None


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
    def delete_task(cls, row_id: int) -> None:
        """Удаляет задачу по ее id"""
        db.delete(cls.table, row_id)

    def update_task(self, row_id: int, raw_message: str) -> Task:
        """Обновляет задачу"""
        column_names = self.column_string.split()
        parsed_message = Tasks._parse_message(raw_message)
        update_dict = {
            column_names[1]: parsed_message.description,
            column_names[2]: parsed_message.date
        }
        db.update(self.table, update_dict, row_id)
        return Task(description=parsed_message.description, date_=parsed_message.date)

    def update_date_task(self, row_id: int, raw_message: str) -> Task:
        """Обновляет только дату задачи"""
        column_names = self.column_string.split()
        parsed_message = Tasks._parse_only_date_message(raw_message)
        update_dict = {
            column_names[2]: parsed_message.date
        }
        db.update(self.table, update_dict, row_id)
        task = db.fetchone(self.table, column_names, row_id)
        return Task(description=task.get('description'), date_=task.get('date_'))

    def update_description_task(self, row_id: int, raw_message: str) -> Task:
        """Обновляет только описание задачи"""
        column_names = self.column_string.split()
        parsed_message = Tasks._parse_message(raw_message)
        update_dict = {
            column_names[1]: parsed_message.description
        }
        db.update(self.table, update_dict, row_id)
        task = db.fetchone(self.table, column_names, row_id)
        return Task(description=task.get('description'), date_=task.get('date_'))

    def add_task(self, raw_message: str) -> Task:
        """Добавляет новую задачу
        Принимает на вход текст сообщения, пришедшего в бот"""
        # разделяет строку столбцов на три, две из которых мы используем в словаре
        column_names = self.column_string.split()
        parsed_message = Tasks._parse_message(raw_message)
        db.insert(self.table, {
            column_names[1]: parsed_message.description,
            column_names[2]: parsed_message.date,
        })
        return Task(description=parsed_message.description, date_=parsed_message.date)

    @staticmethod
    def _parse_message(raw_message: str) -> Message:
        """Парсит текст пришедшего сообщения о задаче."""
        regexp_result = re.match(r"(\d{,2}[./-]\d{,2}[./-]?\d{0,4}) (.*)", raw_message.strip())
        if not regexp_result:
            date_match = re.match(r"(\d{,2}[./-]\d{,2}[./-]?\d{0,4})", raw_message.strip())
            if not date_match:
                task_date = None
                task_text = raw_message.strip()
            else:
                raise exceptions.NotCorrectMessage('Вижу только дату. Отсутствует описание задачи. Нужно описание.\n'
                                                   'Да! Нужно!')
        else:
            if not regexp_result.group(0) \
                    or not regexp_result.group(1) or not regexp_result.group(2):
                raise exceptions.NotCorrectMessage(
                    "Не могу понять сообщение.\n "
                    "Пиши в нужном формате без даты или с ней. \n"
                    "Дату в формате dd.mm.yy - можно использовать разделители, но только один тип: './-', "
                    "например:\n12.12.2020 Классная задача по гачимучи"
                    "\nКлассная задача по гачимучи"
                    "\n12/2/21 Классная задача по гачимучи")
            task_date = Tasks._format_date_with_validate(regexp_result.group(1))
            task_text = regexp_result.group(2).strip()
        return Message(date=task_date, description=task_text)

    @staticmethod
    def _parse_only_date_message(raw_message: str) -> Message:
        """Парсит дату пришедшего сообщения о задаче."""
        date_match = re.match(r"(\d{,2}[./-]\d{,2}[./-]?\d{0,4})", raw_message.strip())
        if not date_match:
            raise exceptions.NotCorrectMessage(
                "Дату в формате dd.mm.yy - можно использовать разделители, но только один тип: './-', "
                "например:\n12.12.2020"
                "\n12/2/21"
                "\n20-04-21")
        else:
            task_date = Tasks._format_date_with_validate(date_match.group(0))
            task_text = None
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
            raise exceptions.NotCorrectMessage('Некоректная дата. Укажите существующую дату.\n'
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
            raise exceptions.NotCorrectMessage('Некоректная дата. Введите дату в формате dd.mm.yy\n'
                                               'Можно использовать разделители, но только один тип: "./-" ')
        return split_date
