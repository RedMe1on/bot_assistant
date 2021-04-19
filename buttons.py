from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# Start menu
button_add_task = KeyboardButton('Добавить задачу')
button_all_tasks = KeyboardButton('Все задачи')
button_today_tasks = KeyboardButton('На сегодня')
button_tomorrow_tasks = KeyboardButton('На завтра')
button_week_tasks = KeyboardButton('На неделю')
button_overdue_tasks = KeyboardButton('Просроченные \U0001F644')
button_tasks_without_deadline = KeyboardButton('Без срока')
button_help = KeyboardButton('Помощь')
button_settings = KeyboardButton('Настройки')

start_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_add_task) \
    .add(button_all_tasks).row(button_today_tasks, button_tomorrow_tasks, button_week_tasks) \
    .row(button_overdue_tasks, button_tasks_without_deadline) \
    .row(button_settings, button_help)

# Cancel menu
button_cancel = KeyboardButton('Отмена')
cancel_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)

# Settings menu
switch_on_switch_off_send_today_task = InlineKeyboardButton('Вкл/Выкл регулярную отправку задач',
                                                            callback_data='switch_on_switch_off_send_today_tasks_in_the_morning')
switch_on_switch_off_send_compliments_and_quotes = InlineKeyboardButton('Вкл/Выкл отправку комплиментов и цитат',
                                                                        callback_data='switch_on_switch_off_send_compliments_and_quotes')
set_morning_time = InlineKeyboardButton('Установить утреннее время', callback_data='set_morning_time')
settings_menu = InlineKeyboardMarkup().add(switch_on_switch_off_send_today_task).add(
    switch_on_switch_off_send_compliments_and_quotes).add(set_morning_time)
