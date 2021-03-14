import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import exceptions
from tasks import Tasks
from utils import StateAddTask

API_TOKEN = '1513442230:AAGZFl5idWxmyxXkTPYwfArTOGraMWp8I-Y'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        "Здарова, Отец!\n\n"
        "Хочешь работы подкинуть? Жми /add_task\n"
        "Рандомную задачку выкинуть: /random\n"
        "Все показать: /all_task\n"
        "Задачи на сегодня: /today_task\n")


@dp.message_handler(state='*', commands=['reset_state'])
async def reset_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['all_task'])
async def send_list_tasks(message: types.Message):
    """Выводит список задач"""
    tasks = Tasks().get_all_tasks()
    result_string = 'Все твои задачи, пупсик:'
    for index, task in enumerate(tasks):
        result_string += f'\n{index + 1}. {task.get("description")} — нажми /del{task.get("id")} для удаления'
    await message.answer(result_string)


@dp.message_handler(state='*', commands=['add_task'])
async def message_for_add_task(message: types.Message):
    """Просит добавить новую задачу"""

    await message.answer("Напиши задачу, например:"
                         "\n12.12.2020 Классная задача по гачимучи"
                         "\nКлассная задача по гачимучи"
                         "\n12.2.21 Классная задача по гачимучи")
    await StateAddTask.add.set()


@dp.message_handler(state=StateAddTask.add)
async def add_task(message: types.Message, state: FSMContext):
    """Добавляет новую задачу"""
    try:
        task = Tasks.add_task(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    if task.date:
        answer_message = (
            f"Задача успешно добавлена.\n"
            f"Дата: {task.date}\n"
            f"Текст задачи: {task.description}")
    else:
        answer_message = (
            f"Задача успешно добавлена.\n"
            f"Текст задачи: {task.description}")
    await message.answer(answer_message)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
