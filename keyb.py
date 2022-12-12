from aiogram import types


def keyb1(button_text):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(len(button_text)):
        key = types.KeyboardButton(text=button_text[i])
        keyboard.add(key)
    return keyboard


def keyb2(button_text, row_with=3):
    keyboard = types.InlineKeyboardMarkup(row_with=row_with)
    for button in button_text:
        key = types.InlineKeyboardButton(button, callback_data=button)
        keyboard.add(key)
    return keyboard


keyb_back = keyb1(["↩️ Назад"])
keyb_standart = keyb1(["Встать в очередь", "Сколько в очeреди?"])
keyb_admin = keyb1(["Встать в очередь", "Сколько в очeреди?", "Статистика", "Кто сейчас?", "Изменить количество ЛП",
                    "Перезапуск бота", "Переименовать ОП"])
