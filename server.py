import asyncio
import json
import random
from datetime import datetime, timedelta
import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound

import exceptions
from buttons import start_menu, settings_menu, cancel_menu
from middlewares import AccessMiddleware
from quotes_and_compliments import Compliments, Quotes
from tasks import Tasks
from utils import StateAddTask, StateSetMorningTime, send_today_tasks_message, validate_morning_time, load_config, \
    change_config, StateUpdateTask

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
ACCESS_ID = os.getenv('TELEGRAM_ACCESS_ID')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        "Ну здарова, Отец!\n\n"
        "Хочешь работы подкинуть? Жми /add_task или напиши Добавь\n"
        "Рандомную задачку выкинуть: /roulette или напиши Рулетка\n"
        "Все показать \U0001F60F: /all_tasks или напиши Все или Список\n"
        "Задачи на сегодня: /today_tasks или напиши Сегодня\n"
        "Задачи на завтра: /tomorrow_tasks или напиши Завтра\n"
        "Задачи на неделю: /week_tasks или напиши Неделя\n"
        "Просроченные задачи (самая частая кнопка - 100%): /overdue_tasks или напиши Просроченные\n"
        "Задачи без даты: /without_deadline или напиши Без даты или Без срока\n"
        "Изменить настройки бота: /settings или напиши Настройки или Настройка\n"
        "Нужна помощь по боту? Жми /help или напиши Помогите или Хелп, или Помощь\n", reply_markup=start_menu)


@dp.message_handler(state='*', commands=['reset_state'])
@dp.message_handler(lambda message: 'Отмена' in message.text, state='*')
async def reset_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.reply('Немножко магии и ты в стартовом меню', reply_markup=start_menu)
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Понял, откатываюсь.', reply_markup=start_menu)


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_tasks(message: types.Message):
    """Удаляет одну задачу по её идентификатору"""
    try:
        task_id = int(message.text[4:])
    except ValueError:
        await message.answer(str(exceptions.NotCorrectMessage('Нет id задачи для удаления')))
        return
    Tasks.delete_task(task_id)
    answer_message = "Задал ей жару! Проверь список, инфа сотка, там ее теперь нет"
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/update'))
async def message_for_update_tasks(message: types.Message, state: FSMContext):
    """Сообщение для обновления задачи по её идентификатору"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Дату ", "Описание")
    markup.add("Отмена")

    try:
        task_id = int(message.text[7:])
    except ValueError:
        await message.answer(str(exceptions.NotCorrectMessage('Нет id задачи для обновления')))
        return
    try:
        task = Tasks().get_one_objects_by_id(task_id)
    except exceptions.ObjectDoesNotExist as e:
        await message.answer(str(e))
        return

    async with state.proxy() as data:
        data['row_id'] = task_id
    if task.get('date_'):
        task_date = task.get('date_')
    else:
        task_date = 'Нет'
    answer_message = (f"Ты хочешь обновить эту задачу:\n"
                      f"Дата: {task_date}\n"
                      f"Текст задачи: {task.get('description')}\n"
                      f"\nЧтобы полностью обновить задачу напиши дату и описание, например:\n"
                      f"\n21.12.2021 Топовая задача для народа"
                      f"\nОтсылка к аниме ДжоДжо"
                      f"\n11.3.22 Не ленись\n"
                      f"\nИли выбери один из вариантов (его можно написать и без клавиатуры, но в точном виде)")
    await message.answer(answer_message, reply_markup=markup)

    await StateUpdateTask.full.set()


@dp.message_handler(lambda message: message.text.lower() == 'дату', state=StateUpdateTask.full)
async def message_for_update_date_tasks(message: types.Message, state: FSMContext):
    """Сообщение о вводе даты для ее обновления"""
    answer_message = "Напиши новую дату"
    await message.answer(answer_message, reply_markup=cancel_menu)
    await StateUpdateTask.date.set()


@dp.message_handler(state=StateUpdateTask.date)
async def update_date_tasks(message: types.Message, state: FSMContext):
    """Обновляет только дату задачи"""
    async with state.proxy() as data:
        try:
            update_only_date_task = Tasks().update_date_task(data['row_id'], message.text)
        except exceptions.NotCorrectMessage as e:
            await message.answer(str(e))
            return
        if update_only_date_task.date_:
            answer_message = (
                f"Дата успешно обновлена!\n"
                f"Дата: {update_only_date_task.date_}\n"
                f"Текст задачи: {update_only_date_task.description}")

        else:
            answer_message = 'Что-то не то! Лучше спросить у создателя'
    await message.answer(answer_message, reply_markup=start_menu)
    await state.finish()


@dp.message_handler(lambda message: message.text.lower() == 'описание', state=StateUpdateTask.full)
async def message_for_update_description_tasks(message: types.Message, state: FSMContext):
    """Сообщение о вводе описания для его обновления"""
    answer_message = "Напиши новое описание. Такое же красивое, как ты \U0001F970"
    await message.answer(answer_message, reply_markup=cancel_menu)
    await StateUpdateTask.description.set()


@dp.message_handler(state=StateUpdateTask.description)
async def update_description_tasks(message: types.Message, state: FSMContext):
    """Обновляет только описание задачи"""
    async with state.proxy() as data:
        try:
            update_only_description_task = Tasks().update_description_task(data['row_id'], message.text)
        except exceptions.NotCorrectMessage as e:
            await message.answer(str(e))
            return
        if update_only_description_task.date_:
            answer_message = (
                f"Описание успешно обновлено!\n"
                f"Дата: {update_only_description_task.date_}\n"
                f"Текст задачи: {update_only_description_task.description}")
        else:
            answer_message = (
                f"Задача успешно обновлена.\n"
                f"Текст задачи: {update_only_description_task.description}")
    await message.answer(answer_message, reply_markup=start_menu)
    await state.finish()


@dp.message_handler(state=StateUpdateTask.full)
async def update_tasks(message: types.Message, state: FSMContext):
    """Обновление задачи по её идентификатору"""
    async with state.proxy() as data:
        try:
            update_task = Tasks().update_task(data['row_id'], message.text)
        except exceptions.NotCorrectMessage as e:
            await message.answer(str(e))
            return
        if update_task.date_:
            answer_message = (
                f"Задача успешно обновлена!\n"
                f"Дата: {update_task.date_}\n"
                f"Текст задачи: {update_task.description}")
        else:
            answer_message = (
                f"Задача успешно обновлена!\n"
                f"Текст задачи: {update_task.description}")
    await message.answer(answer_message, reply_markup=start_menu)
    await state.finish()


@dp.message_handler(commands=['all_tasks'])
@dp.message_handler(lambda message: 'все' in message.text.lower() or 'спис' in message.text.lower())
async def send_list_tasks(message: types.Message):
    """Выводит список задач"""
    tasks = Tasks().get_all_objects()
    if len(tasks) != 0:
        answer_message = 'Все твои задачи, пупсик:\n'
        for index, task in enumerate(tasks):
            if task.get('date_'):
                answer_message += f'\n<b>{index + 1}.</b> {task.get("description")} \nДата: {task.get("date_")}\n ' \
                                  f'\nУдалить: /del{task.get("id")}\n' \
                                  f'Обновить: /update{task.get("id")}\n'
            else:
                answer_message += f'\n<b>{index + 1}.</b> {task.get("description")}\n' \
                                  f'\nУдалить: /del{task.get("id")}\n' \
                                  f'Обновить: /update{task.get("id")}\n'
    else:
        answer_message = 'Никаких задач на сегодня нет. Добавь себе парочку! Не стесняйся, заставлять делать не буду :)'
    await message.answer(answer_message)


@dp.message_handler(commands=['roulette'])
@dp.message_handler(lambda message: 'рулет' in message.text.lower())
async def send_random_tasks(message: types.Message):
    """Выводит рандомную задачу"""
    random_task = Tasks().get_random_object()
    if random_task:
        answer_message = 'Боги рандома дают тебе:\n'
        answer_message += f'\n{random_task.get("description")}\n' \
                          f'\nУдалить: /del{random_task.get("id")}\n' \
                          f'Обновить: /update{random_task.get("id")}\n'
    else:
        answer_message = 'Нет рандомной задачи, потому что задач нет, но если ты добавишь одну, две или три, то в этом казино будет смысл'
    await message.answer(answer_message)


@dp.message_handler(commands=['today_tasks'])
@dp.message_handler(lambda message: 'сегод' in message.text.lower())
async def send_today_tasks(message: types.Message):
    """Выводит задачи на сегодня"""
    result_string = send_today_tasks_message()
    await message.answer(result_string)


@dp.message_handler(commands=['tomorrow_tasks'])
@dp.message_handler(lambda message: 'завт' in message.text.lower())
async def send_tomorrow_tasks(message: types.Message):
    """Выводит задачи на завтра"""
    tomorrow_tasks = Tasks().get_tasks_with_days_interval(1)
    if len(tomorrow_tasks) != 0:
        result_string = 'Завтра у тебя много работы, прям завал:\n'
        for index, task in enumerate(tomorrow_tasks):
            result_string += f'\n<b>{index + 1}.</b> {task.get("description")}\n' \
                             f'\nУдалить: /del{task.get("id")}\n' \
                             f'Обновить: /update{task.get("id")}\n'
    else:
        result_string = 'Придумай, что делать завтра, потому что список задач на завтра ПУСТ! (как и мой интеллект)'
    await message.answer(result_string)


@dp.message_handler(commands=['week_tasks'])
@dp.message_handler(lambda message: 'недел' in message.text.lower())
async def send_list_tasks_during_the_week(message: types.Message):
    """Выводит задачи на неделю"""
    week_task = Tasks().get_tasks_with_days_interval(7)
    if len(week_task) != 0:
        result_string = 'Задачи на неделю вперед ждут, пока ты их сделаешь когда-нибудь потом. На, посмотри на них:\n'
        for index, task in enumerate(week_task):
            result_string += f'<b>\n{index + 1}.</b> {task.get("description")} \nДата: {task.get("date_")}\n ' \
                             f'\nУдалить: /del{task.get("id")}\n' \
                             f'Обновить: /update{task.get("id")}\n'
    else:
        result_string = 'Неделя обещает быть максимально удачной! У тебя нет задач, их 0. \n' \
                        'Покрути рулетку или добавь себе работы!'
    await message.answer(result_string)


@dp.message_handler(commands=['overdue_tasks'])
@dp.message_handler(lambda message: 'просро' in message.text.lower())
async def send_list_overdue_tasks(message: types.Message):
    """Выводит просроченные задачи"""
    overdue_task = Tasks().get_overdue_tasks()
    if len(overdue_task) != 0:
        result_string = 'Мда, всегда откладываешь на завтра? Я тоже :)\n' \
                        'Да когда-нибудь потом сделаешь, что уж там. \n' \
                        'Но, если это когда-нибудь сейчас, то вот тебе список:\n'
        for index, task in enumerate(overdue_task):
            result_string += f'\n<b>{index + 1}.</b> {task.get("description")} \nДата: {task.get("date_")}\n ' \
                             f'\nУдалить: /del{task.get("id")}\n' \
                             f'Обновить: /update{task.get("id")}\n'
    else:
        result_string = 'Вот это я понимаю, никаких просроченных задач. Ты молодец!\n' \
                        'Я тоже люблю ставить задачи без сроков, либо удалять те, что не успел выполнить ;)'
    await message.answer(result_string)


@dp.message_handler(commands=['without_deadline'])
@dp.message_handler(lambda message: 'без срок' in message.text.lower() or 'без дат' in message.text.lower())
async def send_list_tasks_without_deadline(message: types.Message):
    """Выводит задачи на сегодня"""
    task_without_deadline = Tasks().get_date_without_deadline()
    if len(task_without_deadline) != 0:
        result_string = 'Не люблю задачи с дедлайнами, поэтому кидаю этот список с любовью:\n'
        for index, task in enumerate(task_without_deadline):
            result_string += f'\n<b>{index + 1}.</b> {task.get("description")}\n' \
                             f'\nУдалить: /del{task.get("id")}\n' \
                             f'Обновить: /update{task.get("id")}\n'
    else:
        result_string = 'Задач без даты не нашел, а ты не из ленивых.\n' \
                        'Чекни полный список! ;)'
    await message.answer(result_string)


@dp.message_handler(state='*', commands=['add_task'])
@dp.message_handler(lambda message: 'добав' in message.text.lower())
async def message_for_add_task(message: types.Message, state: FSMContext):
    """Просит добавить новую задачу"""
    await message.answer("Напиши задачу, например:"
                         "\n12.12.2020 Классная задача по гачимучи"
                         "\nКлассная задача по гачимучи"
                         "\n12.2.21 Классная задача по гачимучи", reply_markup=cancel_menu)
    await StateAddTask.add.set()


@dp.message_handler(state=StateAddTask.add)
async def add_task(message: types.Message, state: FSMContext):
    """Добавляет новую задачу"""
    try:
        task = Tasks().add_task(message.text)
    except exceptions.NotCorrectMessage as e:
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
    await message.answer(answer_message, reply_markup=start_menu)
    await state.finish()


@dp.message_handler(commands=['settings'])
@dp.message_handler(lambda message: 'настрой' in message.text.lower())
async def set_settings(message: types.Message):
    """Выводит инлайн клавиатуру с настройками"""
    result_string = 'Выбери нужную настройку:\n' \
                    '1. Вкл/Выкл регулярную отправку задач - включает и отключает ' \
                    'ежедневную отправку задач на сегодня\n' \
                    '2. Вкл/Выкл отправку комплиментов и цитат - включает и отключает ' \
                    'ежедневную отправку комплиментов и цитат\n ' \
                    '3. Установить утреннее время - устанавливает час, ' \
                    'в который бот будет отправлять задачи на сегодня. Ожидает число от 0 до 23\n'
    await message.answer(result_string, reply_markup=settings_menu)


@dp.callback_query_handler(lambda c: c.data == 'switch_on_switch_off_send_today_tasks_in_the_morning')
async def switch_on_switch_off_send_today_tasks_in_the_morning(callback_query: types.CallbackQuery):
    """Настройка для включения и выключения отправки ежедневных задач"""
    config = load_config()
    if config['send_today_tasks_in_the_morning']:
        config['send_today_tasks_in_the_morning'] = False
        change_config(config)
        text_msg = 'Выключил!'
    else:
        config['send_today_tasks_in_the_morning'] = True
        change_config(config)
        text_msg = 'Включил!'

    await bot.answer_callback_query(callback_query.id, text=text_msg)


@dp.callback_query_handler(lambda c: c.data == 'switch_on_switch_off_send_compliments_and_quotes')
async def switch_on_switch_off_send_compliment_and_quotes(callback_query: types.CallbackQuery):
    """Настройка для включения и выключения отправки комплиментов или цитат"""
    config = load_config()
    if config['send_compliments_and_quotes']:
        config['send_compliments_and_quotes'] = False
        change_config(config)
        text_msg = 'Выключил!'
    else:
        config['send_compliments_and_quotes'] = True
        change_config(config)
        text_msg = 'Включил!'

    await bot.answer_callback_query(callback_query.id, text=text_msg)


@dp.callback_query_handler(lambda c: c.data == 'set_morning_time', state='*')
async def message_for_set_morning_time(callback_query: types.CallbackQuery):
    """Запрос ввода числа для утреннего времени"""
    config = load_config()
    text_msg = f'С какого хе..., часа начинать отправлять задачи на сегодня?\nСейчас: {int(config["morning_hour"])}'

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, text_msg, reply_markup=cancel_menu)
    await StateSetMorningTime.set.set()


@dp.message_handler(state=StateSetMorningTime.set)
async def set_morning_time(message: types.Message, state: FSMContext):
    """Хендлер для настройки утреннего времени"""
    config = load_config()
    try:
        config['morning_hour'] = validate_morning_time(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.reply(str(e))
        return
    change_config(config)
    text_msg = f'Теперь буду отправлять к этому часу: {config["morning_hour"]}'
    await message.answer(text_msg, reply_markup=start_menu)
    await set_settings(message)
    await state.finish()


@dp.message_handler(commands=['help'])
@dp.message_handler(lambda
                            message: 'помогит' in message.text.lower() or 'хелп' in message.text.lower() or 'помощь' in message.text.lower())
async def send_help(message: types.Message):
    """Отправляет помощь и документацию по боту"""
    await message.answer(
        'Пояснительная бригада тут!\n\n'
        'Все слова и фразы можно писать в рандомном контексте и склонениях (почти всех, наверное):\n'
        '"Тупой раб, добавь задачу"\n'
        '"Мне нужно добавить задачу"\n'
        '"Рулетку бы сегодня" - выдаст рулетку\n'
        '"Что у нас сегодня по задачам?" - выдаст список задач на сегодня и т.д.\n'
        'Надеюсь, понятно объяснил, теперь хватит примеров, фигачим команды:\n\n'
        '/add_task - Добавляет задачу, можно вызывать словом "добавить"\n'
        '/all_tasks - Показывает все задачи, можно вызывать словом "все" или "список"\n'
        '/roulette - Выдает рандомную задачу, можно вызывать словом "рулетка"\n'
        '/today_tasks - Список задач на сегодня, можно вызывать словом "сегодня"\n'
        '/tomorrow_tasks - Список задач на завтра, можно вызывать словом "завтра"\n'
        '/week_tasks - Список задач на неделю, можно вызывать словом "неделя"\n'
        '/overdue_tasks - Список просроченных задач, можно вызывать словом "просроченные"\n'
        '/without_deadline - Список задач без даты, можно вызвать фразой "без даты" или "без срока"\n'
        '/settings - Вызывает меню настроек бота, можно вызвать фразой "настройка"\n'
        '/reset_state - Возвращает к первоначальному меню откуда хочешь :), можно вызывать словом "отмена"\n',
        reply_markup=start_menu)


async def send_compliments_or_quotes(time_before_send_message: int):
    """Отправляет сообщение с комплиментом или цитатой"""
    try:
        await asyncio.sleep(time_before_send_message)
        compliments_or_quotes = random.random()
        if compliments_or_quotes < 0.7:
            quotes = Quotes()
            random_quote = quotes.get_random_object()
            await bot.send_message(ACCESS_ID, f"{random_quote['text']} \n"
                                              f"<i>—{random_quote['author']}</i>")
        else:
            compliments = Compliments()
            random_compliment = compliments.get_random_object()
            await bot.send_message(ACCESS_ID, f"{random_compliment['text']}")
    except ChatNotFound:
        logging.info('Chat not found. Waiting for.')
        await asyncio.sleep(86400)


async def send_today_tasks_in_the_morning():
    """Отправляет задачи за сегодня раз в день"""
    while True:
        try:
            config = load_config()
            if config['send_today_tasks_in_the_morning']:
                hour = datetime.now().time().hour
                if hour == config['morning_hour']:
                    await bot.send_message(ACCESS_ID, send_today_tasks_message())
                    await asyncio.sleep(86400)
                else:
                    await asyncio.sleep(600)
            else:
                await asyncio.sleep(86400)
        except ChatNotFound:
            logging.info('Chat not found. Waiting for.')
            await asyncio.sleep(86400)


async def check_time(start_time: int, end_time: int):
    """Следит, чтобы сообщения были отправлены в нужный интервал времени"""
    while True:
        config = load_config()
        if config['send_compliments_and_quotes']:
            hour = datetime.now().time().hour
            if start_time <= hour < end_time:
                time_to_end_interval = (timedelta(hours=(end_time - hour))).total_seconds()
                random_time_for_send_message = random.randint(1, time_to_end_interval)
                await send_compliments_or_quotes(random_time_for_send_message)
                await asyncio.sleep(time_to_end_interval - random_time_for_send_message)
            else:
                await asyncio.sleep(3600)
        else:
            await asyncio.sleep(86400)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_time(start_time=9, end_time=22))
    loop.create_task(send_today_tasks_in_the_morning())
    executor.start_polling(dp, skip_updates=True)
