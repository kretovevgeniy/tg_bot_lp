from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
from datetime import timedelta


def add_buttons(text, callback_data):
    inline_kb1.insert(InlineKeyboardButton(text=text, callback_data=callback_data))


def null_inline_kb1():
    global inline_kb1
    inline_kb1 = InlineKeyboardMarkup(row_width=7)


inline_kb1 = InlineKeyboardMarkup(row_width=7)
day = timedelta(days=1)
firstDateResult = None
lastDateResult = None


def get_first_date():
    first_date = datetime.datetime.now().date() - 30 * day
    week_day = first_date.weekday()
    return first_date, week_day


def add_day(in_day, count):
    new_date = in_day + count * day
    full_date = str(new_date.strftime('%Y') + '-' + new_date.strftime('%m') + '-' + new_date.strftime('%d'))
    date = str(new_date.strftime('%d') + '.' + new_date.strftime('%m'))
    return full_date, date


def create_inlineKM():
    weekRow = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    firstDateInCalendar, firstWeekDate = get_first_date()
    for weekday in weekRow:
        add_buttons(weekday, 'None')
    for none_pre_days in range(firstWeekDate):
        add_buttons(' ', 'None')
    for _day in range(31):
        full_day, date_text = add_day(firstDateInCalendar, _day)
        add_buttons(date_text, f'day{date_text}{full_day}{_day}')
    if firstWeekDate < 5:
        shift = 4
    else:
        shift = 10
    for none_post_days in range(shift - firstWeekDate):
        add_buttons(' ', 'None')


def get_mass_dates(first_day, last_day, shift):
    datetime_first_day = datetime.datetime.strptime(first_day, '%Y-%m-%d').date()
    datetime_last_day = datetime.datetime.strptime(last_day, '%Y-%m-%d').date()
    result_mass = [datetime_first_day]
    new_date = datetime_first_day
    for date in range(shift):
        new_date += day
        result_mass.append(new_date)
    assert result_mass[-1] == datetime_last_day
    return result_mass
