from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

button_add_task = KeyboardButton('Добавить задачу! 👋')
button_all_task = KeyboardButton('Все задачи! 👋')
button_today_task = KeyboardButton('Задачи на сегодня! 👋')
button_tomorrow_task = KeyboardButton('Задачи на завтра! 👋')

start_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_add_task).add(button_all_task).row(button_today_task,
                                                                                                     button_tomorrow_task)

button_cancel = KeyboardButton('Отмена! 👋')
add_task_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)

