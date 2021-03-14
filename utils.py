from aiogram.dispatcher.filters.state import State, StatesGroup


class StateAddTask(StatesGroup):
    """Состояния при добавлении задачи"""
    add = State()
