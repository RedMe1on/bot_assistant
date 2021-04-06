from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

button_add_task = KeyboardButton('Добавить задачу')
button_all_task = KeyboardButton('Все задачи')
button_today_task = KeyboardButton('На сегодня')
button_tomorrow_task = KeyboardButton('На завтра')
button_week_task = KeyboardButton('На неделю')
button_overdue_task = KeyboardButton('Просроченные \U0001F644')
button_help = KeyboardButton('Помощь')

start_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_add_task) \
    .add(button_all_task).row(button_today_task, button_tomorrow_task, button_week_task) \
    .row(button_overdue_task, button_help)

button_cancel = KeyboardButton('Отмена')
add_task_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)
