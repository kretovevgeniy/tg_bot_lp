from aiogram import types


def keyb1(button_text):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(len(button_text)):
        key = types.KeyboardButton(text=button_text[i])
        keyboard.add(key)
    return keyboard