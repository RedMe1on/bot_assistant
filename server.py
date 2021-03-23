import asyncio
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
        "Рандомную задачку выкинуть: /roulette\n"
        "Все показать: /all_task\n"
        "Задачи на сегодня: /today_task\n")


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_tasks(message: types.Message):
    """Удаляет одну задачу по её идентификатору"""
    row_id = int(message.text[4:])
    Tasks.delete_task(row_id)
    answer_message = "Задал ей жару! Проверь список, инфа сотка, там ее теперь нет"
    await message.answer(answer_message)
    await send_list_tasks(message)


@dp.message_handler(state='*', commands=['reset_state'])
@dp.message_handler(lambda message: 'назад' in message.text.lower() or 'отмен' in message.text.lower())
async def reset_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['all_task'])
@dp.message_handler(lambda message: 'все' in message.text.lower() or 'спис' in message.text.lower())
async def send_list_tasks(message: types.Message):
    """Выводит список задач"""
    tasks = Tasks().get_all_tasks()
    result_string = 'Все твои задачи, пупсик:'
    for index, task in enumerate(tasks):
        if task.get('date_'):
            result_string += f'\n{index + 1}. {task.get("description")} \nДата: {task.get("date_")} ' \
                             f'\nУдалить: /del{task.get("id")}'
        else:
            result_string += f'\n{index + 1}. {task.get("description")}' \
                             f'\nУдалить: /del{task.get("id")}'
    await message.answer(result_string)


@dp.message_handler(commands=['roulette'])
@dp.message_handler(lambda message: 'рулет' in message.text.lower())
async def send_random_tasks(message: types.Message):
    """Выводит рандомную задачу"""
    random_task = Tasks().get_random_task()
    result_string = 'И тебе ВЫПАДААААЕЕЕЕТ:'
    result_string += f'\n{random_task.get("description")}' \
                     f'\nУдалить: /del{random_task.get("id")}'
    await message.answer(result_string)


@dp.message_handler(commands=['today_task'])
@dp.message_handler(lambda message: 'сегод' in message.text.lower())
async def send_today_tasks(message: types.Message):
    """Выводит задачи на сегодня"""
    today_task = Tasks().get_tasks_with_days_interval(0)
    if len(today_task) != 0:
        result_string = 'Сегодня у тебя много работы, прям завал:'
        for index, task in enumerate(today_task):
            result_string += f'\n{index + 1}. {task.get("description")}' \
                             f'\nУдалить: /del{task.get("id")}'
    else:
        result_string = 'Ты сегодня самый занятой человек планеты, у тебя целых 0 задач на сегодня!\n' \
                        'Лучше попроси парочку из полного списка или добавь себе работы!'
    await message.answer(result_string)


@dp.message_handler(commands=['tomorrow_task'])
@dp.message_handler(lambda message: 'завт' in message.text.lower())
async def send_tomorrow_tasks(message: types.Message):
    """Выводит задачи на сегодня"""
    today_task = Tasks().get_tasks_with_days_interval(1)
    if len(today_task) != 0:
        result_string = 'Завтра у тебя много работы, прям завал:'
        for index, task in enumerate(today_task):
            result_string += f'\n{index + 1}. {task.get("description")}' \
                             f'\nУдалить: /del{task.get("id")}'
    else:
        result_string = 'Придумай, что делать завтра, потому что список задач на завтра ПУСТ! (как и мой интеллект)'
    await message.answer(result_string)


@dp.message_handler(commands=['week_task'])
@dp.message_handler(lambda message: 'недел' in message.text.lower())
async def send_list_tasks_during_the_week(message: types.Message):
    """Выводит задачи на сегодня"""
    today_task = Tasks().get_tasks_with_days_interval(1)
    if len(today_task) != 0:
        result_string = 'Задачи на неделю вперед ждут, пока ты их сделаешь когда-нибудь потом. На, посмотри на них:'
        for index, task in enumerate(today_task):
            result_string += f'\n{index + 1}. {task.get("description")} \nДата: {task.get("date_")} ' \
                             f'\nУдалить: /del{task.get("id")}'
    else:
        result_string = 'Неделя обещает быть максимально удачной! У тебя нет задач, их 0. \n' \
                        'Покрути рулетку или добавь себе работы!'
    await message.answer(result_string)


@dp.message_handler(state='*', commands=['add_task'])
@dp.message_handler(lambda message: 'добав' in message.text.lower())
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
    except exceptions.NotCorrectData as e:
        await message.answer(str(e))
        return
    if task.date_:
        answer_message = (
            f"Задача успешно добавлена.\n"
            f"Дата: {task.date_}\n"
            f"Текст задачи: {task.description}")
    else:
        answer_message = (
            f"Задача успешно добавлена.\n"
            f"Текст задачи: {task.description}")
    await message.answer(answer_message)
    await state.finish()





# async def my_func():
#     # твоя логика с отправкой сообщений тут
#     print('hi, father')
#     when_to_call = loop.time() + delay  # delay -- промежуток времени в секундах.
#     loop.call_at(when_to_call, my_callback)
#
#
# def my_callback():
#     asyncio.create_task(my_func())
#
#
# # async def gg():
# #     while True:
# #         await bot.send_message(567115076, 'test')
# #         await asyncio.sleep(10)


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # delay = 10.0
    # loop.run_until_complete(my_callback())
    executor.start_polling(dp, skip_updates=True)
    # loop.run_forever()


