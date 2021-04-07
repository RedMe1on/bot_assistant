from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

button_add_task = KeyboardButton('Добавить задачу')
button_all_tasks = KeyboardButton('Все задачи')
button_today_tasks = KeyboardButton('На сегодня')
button_tomorrow_tasks = KeyboardButton('На завтра')
button_week_tasks = KeyboardButton('На неделю')
button_overdue_tasks = KeyboardButton('Просроченные \U0001F644')
button_tasks_without_deadline = KeyboardButton('Без срока')
button_help = KeyboardButton('Помощь')

start_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_add_task) \
    .add(button_all_tasks).row(button_today_tasks, button_tomorrow_tasks, button_week_tasks) \
    .row(button_overdue_tasks, button_tasks_without_deadline, button_help)

button_cancel = KeyboardButton('Отмена')
add_task_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)
