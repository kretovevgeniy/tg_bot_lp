# ЗАДАЧИ: придумать, как передавать id правил между методами и сделать увеличение лимита на 2 и более
import sqlite3
import asyncio
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.utils.exceptions import NetworkError
from datetime import datetime, timedelta
import arry
import oper
from keyb import keyb1, keyb2, keyb_standart, keyb_admin, keyb_back
import make_calendar

# Бот2 900114919:AAFPw4KkBeit5Sa4FCO2sE5z-6sSAqPMcNM
# happy kz 5589930594:AAGMOYcTTYFA1etzKdihcyM9-H2yQfegHTs
bot = Bot(token='900114919:AAFPw4KkBeit5Sa4FCO2sE5z-6sSAqPMcNM')
dp = Dispatcher(bot, storage=MemoryStorage())


class States(StatesGroup):
    waiting_fio = State()
    new_admin = State()
    remove_admin = State()
    main_statistic = State()
    op_statistic = State()
    set_lp = State()
    tech = State()
    restart_bot = State()
    rename_1 = State()
    rename_2 = State()
    rename_3 = State()
    new_name = State()
    rules_start = State()
    rules_time_start = State()
    rules_time_finish = State()
    rules_2 = State()
    rules_start_now = State()
    rules_limit = State()


def db():
    con = sqlite3.connect("kz_lp.db")
    cur = con.cursor()
    # cur.execute('DROP TABLE test2')
    cur.execute('CREATE TABLE IF NOT EXISTS operators(fio TEXT, chat_id INTEGER, que TEXT, pre_start TEXT, start TEXT, '
                'chat TEXT, date DATE, username TEXT, ready BOOLEAN)')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS fio_id(id INTEGER PRIMARY KEY, Fio TEXT NOT NULL, chat_id INTEGER NOT NULL)')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS admin(chat_id INTEGER NOT NULL)')


def my_lower_sql(s):
    return s.lower()


async def db_in_fio(input_mass):
    con = sqlite3.connect("kz_lp.db")
    cur = con.cursor()
    cur.execute(f'INSERT INTO fio_id(fio, chat_id) VALUES(?, ?)', input_mass)
    con.commit()
    cur.close()


async def db_in_op(input_mass):
    con = sqlite3.connect("kz_lp.db")
    cur = con.cursor()
    cur.execute(f'INSERT INTO operators(fio, chat_id, que, pre_start, start, chat, date, username, ready) '
                f'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', input_mass)
    con.commit()
    cur.close()


async def db_in_admin(input_mass):
    con = sqlite3.connect("kz_lp.db")
    cur = con.cursor()
    cur.execute(f'INSERT INTO admin(chat_id) VALUES(?)', input_mass)
    con.commit()
    cur.close()


async def db_out(db_name, column="*", filter_sql=None, one_element=True):
    con = sqlite3.connect("kz_lp.db")
    con.create_function('my_lower', 1, my_lower_sql)
    cur = con.cursor()
    if filter_sql is None:
        query = f'SELECT {column} FROM {db_name}'
    else:
        query = f'SELECT {column} FROM {db_name} WHERE {filter_sql}'
    cur.execute(query)
    data = cur.fetchone() if one_element else cur.fetchall()
    con.commit()
    cur.close()
    return data


async def db_upd(db_name, columns, new_data, filter_sql):
    # example columns = 'fio = ? , chat_id = ? '
    con = sqlite3.connect("kz_lp.db")
    cur = con.cursor()
    query = f'UPDATE {db_name} SET {columns} WHERE {filter_sql}'
    cur.execute(query, new_data)
    con.commit()
    cur.close()


async def db_del(db_name, filter_sql):
    con = sqlite3.connect("kz_lp.db")
    cur = con.cursor()
    query = f'DELETE FROM {db_name} WHERE {filter_sql}'
    cur.execute(query)
    con.commit()
    cur.close()


# https://teletype.in/@codingcommunity/SyKLWZ154


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if await db_out('fio_id', filter_sql=f'chat_id = {message.chat.id}') is not None:
        await bot.send_message(292075774, f"попытка start. ID {message.chat.id}")
        return
    await message.answer(f'Привет, {message.from_user.first_name}! Это бот по ЛП. Напиши, пожалуйста одним сообщением '
                         f'свою реальную фамилию и реальное имя.', reply_markup=types.ReplyKeyboardRemove())
    await States.waiting_fio.set()


@dp.message_handler(state=States.waiting_fio)
async def set_fio(message: types.Message, state: FSMContext):
    input_mass = [message.text, message.chat.id]
    await db_in_fio(input_mass)
    keyb = keyb_admin if message.chat.id in arry.person else keyb_standart
    await message.answer(f'Приятно познакомиться, {message.text} :)\nТеперь ты можешь пользоваться моим функционалом.',
                         reply_markup=keyb)
    await state.finish()


async def main_statistic_1(message: types.Message, state: FSMContext):
    make_calendar.create_inlineKM()
    async with state.proxy() as data:
        data['firstDateFull'] = None
        data['chat_id'] = message.chat.id
    await message.answer('За какой день нужна статистика?',
                         reply_markup=make_calendar.inline_kb1)


@dp.message_handler(state=States.op_statistic)
async def main_statistic_2(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Чем могу помочь?",
                             reply_markup=keyb_admin)
        await state.finish()
        return

    async def send(i):
        text = f'ФИО: {i[0]} \nДата: {i[6]}\nВстал в очередь в {i[2]} \nВышел в перед обедом в {i[3]} ' \
               f'\nВышел в ЛП в {i[4]} \nВернулся в чаты в {i[5]} \nUsername: {i[7]}'
        await message.answer(text)

    async def send_2():
        await message.answer("Чем еще могу помочь? :)", reply_markup=keyb_admin)

    async with state.proxy() as data:
        firstDateFull = data['firstDateFull']
        firstDateCode = data['firstDateCode']
        lastDateFull = data['lastDateFull']
        lastDateCode = data['lastDateCode']
    shift_days = int(lastDateCode) - int(firstDateCode)
    dates = make_calendar.get_mass_dates(firstDateFull, lastDateFull, shift_days)
    if message.text == "Нужна статистика по всем операторам":
        result_mass_is_null = True
        for date in dates:
            res_mass = await db_out('operators', filter_sql=f'date = \'{str(date)}\'', one_element=False)
            if len(res_mass) != 0:
                result_mass_is_null = False
            for operator in res_mass:
                await send(operator)
        if result_mass_is_null:
            await message.answer("Записей нет :(")
        await send_2()
    elif message.forward_date is not None:
        try:
            id_ = message.forward_from.id
        except:
            await message.answer("Не получается определить ID аккаунта. Скорее всего, настройки приватности оператора "
                                 "не позволяют выяснить его ID. Попроси, пожалуйста, оператора внести этого бота в "
                                 "исключения в разделе \"Настройки\" -> \"Конфиденциальность\" -> \"Пересылка "
                                 "сообщений\"", reply_markup=keyb_admin)
            await state.finish()
            return
        result_mass_is_null = True
        for date in dates:
            res_mass = await db_out('operators', filter_sql=f'date = \'{str(date)}\' and chat_id = {id_}',
                                    one_element=False)
            if len(res_mass) != 0:
                result_mass_is_null = False
            for operator in res_mass:
                await send(operator)
        if result_mass_is_null:
            await message.answer("Записей нет :(")
        await send_2()
    else:
        fio = message.text.lower()
        result_mass_is_null = True
        for date in dates:
            res_mass = await db_out('operators', filter_sql=f'date= \'{str(date)}\' AND my_lower(fio) LIKE \'%{fio}%\'',
                                    one_element=False)
            if len(res_mass) != 0:
                result_mass_is_null = False
            for operator in res_mass:
                await send(operator)
        if result_mass_is_null:
            await message.answer("Записей нет :(")
        await send_2()
    await state.finish()


async def pre_lp(chat_id):
    arry.buf_op[chat_id].ready = True
    await asyncio.sleep(5)
    while True:
        try:
            if chat_id in arry.pre_lp:
                arry.buf_op[chat_id].ready = False
                await bot.send_message(chat_id, "Эгегей, надеюсь, чаты уже закрыты, пошло время ЛП.",
                                       reply_markup=keyb1(["Дoсрочно выйти с ЛП"]))
                arry.buf_op[chat_id].start = datetime.now()
            break
        except NetworkError:
            await asyncio.sleep(5)
            print('try pre_lp 5 sec')


async def lp(chat_id, state: FSMContext):
    arry.buf_op[chat_id].ready = True
    await asyncio.sleep(10)
    while True:
        try:
            if chat_id in arry.lp:
                arry.buf_op[chat_id].ready = False
                keyb = keyb_admin if chat_id in arry.person else keyb_standart
                await bot.send_message(chat_id, "ЛП закончился, выходи в чаты.", reply_markup=keyb)
                arry.lp.remove(chat_id)
                arry.buf_op[chat_id].chat = datetime.now().strftime("%H:%M:%S")
                arry.buf_op[chat_id].start = arry.buf_op[chat_id].start.strftime("%H:%M:%S")
                arry.buf_op[chat_id].pre_start = arry.buf_op[chat_id].pre_start.strftime("%H:%M:%S")
                arry.buf_op[chat_id].date = datetime.now().date()
                await db_in_op(oper.Oper.to_mass_for_sql(arry.buf_op[chat_id]))
                del arry.buf_op[chat_id]
                if len(arry.queu) > 0 and len(arry.lp) + len(arry.pre_lp) <= arry.lp_now - 1:
                    await start_lp(arry.queu[0], state)
            break
        except NetworkError:
            await asyncio.sleep(5)
            print('try lp 5 sec')


async def start_lp(chat_id, state: FSMContext):
    arry.buf_op[chat_id].pre_start = datetime.now()
    text = "Оказывается, очередь как раз скоро подойдет! Выходи в \"перед обедом\" и закрывай чаты :)"
    await bot.send_message(chat_id, text, reply_markup=keyb1(["Зaкрыл(-а) чаты"]))
    arry.queu.remove(chat_id)
    arry.pre_lp.append(chat_id)
    await pre_lp(chat_id)
    if chat_id in arry.pre_lp:
        arry.pre_lp.remove(chat_id)
        arry.lp.append(chat_id)
        await lp(chat_id, state)


async def who_now(chat_id):
    lp_mass = arry.lp
    pre_lp_mass = arry.pre_lp
    qu_mass = arry.queu
    if len(lp_mass) > 0:
        lp_text = ""
        for i in range(len(lp_mass)):
            a = datetime.now() - arry.buf_op[lp_mass[i]].start
            lp_text += f'\n{arry.buf_op[lp_mass[i]].fio} {timedelta(seconds=int(a.total_seconds()))}'
        lp_text1 = f'В ЛП: {lp_text}'
    else:
        lp_text1 = 'В ЛП никого'
    await bot.send_message(chat_id, lp_text1)
    if len(pre_lp_mass) > 0:
        pre_lp_text = ""
        for i in range(len(pre_lp_mass)):
            a = datetime.now() - arry.buf_op[pre_lp_mass[i]].pre_start
            pre_lp_text += f'\n{arry.buf_op[pre_lp_mass[i]].fio} {timedelta(seconds=int(a.total_seconds()))}'
        pre_lp_text1 = f'В перед обедом: {pre_lp_text}'
    else:
        pre_lp_text1 = "В перед обедом никого"
    await bot.send_message(chat_id, pre_lp_text1)
    if len(qu_mass) > 0:
        qu_text = ""
        for i in range(len(qu_mass)):
            qu_text += f'\n{arry.buf_op[qu_mass[i]].fio} с {arry.buf_op[qu_mass[i]].que}'
        qu_text1 = f'В очереди: {qu_text}'
    else:
        qu_text1 = "В очереди никого"
    await bot.send_message(chat_id, qu_text1)


@dp.message_handler(state=States.set_lp)
async def set_lp(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?",
                             reply_markup=keyb_admin)
        await state.finish()
        return
    '''
    async def add_lp():
        await asyncio.create_task(start_lp(arry.queu[0], state))
        await asyncio.create_task(start_lp(arry.queu[0], state))
    '''
    old_lp = arry.lp_now
    await state.finish()
    if message.text == "Увеличить на 1":
        arry.lp_now += 1
        await message.answer(f'Количество одновременных ЛП изменилось. Новое значение: {arry.lp_now}',
                             reply_markup=keyb_admin)
        op = oper.Oper(f'@{message.chat.username}', 0, old_lp, arry.lp_now, datetime.now().strftime("%H:%M:%S"),
                       date=datetime.now().date())
        await db_in_op(oper.Oper.to_mass_for_sql(op))
        await start_lp(arry.queu[0], state)
    elif message.text == 'Уменьшить на 1':
        arry.lp_now -= 1
        await message.answer(f'Количество одновременных ЛП изменилось. Новое значение: {arry.lp_now}',
                             reply_markup=keyb_admin)
        op = oper.Oper(f'@{message.chat.username}', 0, old_lp, arry.lp_now, datetime.now().strftime("%H:%M:%S"),
                       date=datetime.now().date())
        await db_in_op(oper.Oper.to_mass_for_sql(op))
    '''
    elif int(message.text) > 0:
        new_lim = int(message.text)
        arry.lp_now = new_lim
        await message.answer(f'Количество одновременных ЛП изменилось. Новое значение: {new_lim}',
                             reply_markup=keyb_admin)
        if new_lim > old_lp:
            asyncio.run(add_lp())
    '''


@dp.message_handler(state=States.new_admin)
async def new_admin(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?",
                             reply_markup=keyb_admin)
        await state.finish()
        return
    try:
        id_tg = message.forward_from.id
    except:
        await message.answer("Не получается определить ID аккаунта. Скорее всего, настройки приватности оператора "
                             "не позволяют выяснить его ID. Попроси, пожалуйста, оператора внести этого бота в "
                             "исключения в разделе \"Настройки\" -> \"Конфиденциальность\" -> \"Пересылка "
                             "сообщений\"", reply_markup=keyb_admin)
        await state.finish()
        return
    arry.person.append(id_tg)
    await db_in_admin([id_tg])
    await message.answer(f'Окей, теперь {message.forward_from.first_name} админ',
                         reply_markup=keyb_admin)
    await bot.send_message(292075774,
                           f'@{message.chat.username} добавил нового админа: @{message.forward_from.username}')
    await bot.send_message(id_tg, "Ты админ", reply_markup=keyb_admin)
    await state.finish()


@dp.message_handler(state=States.remove_admin)
async def remove_admin(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?",
                             reply_markup=keyb_admin)
        await state.finish()
        return
    try:
        id_tg = message.forward_from.id
    except:
        await message.answer("Не получается определить ID аккаунта. Скорее всего, настройки приватности оператора "
                             "не позволяют выяснить его ID. Попроси, пожалуйста, оператора внести этого бота в "
                             "исключения в разделе \"Настройки\" -> \"Конфиденциальность\" -> \"Пересылка "
                             "сообщений\"", reply_markup=keyb_admin)
        await state.finish()
        return
    if id_tg not in arry.person:
        await state.finish()
        return
    arry.person.remove(id_tg)
    await db_del('admin', f'chat_id = {id_tg}')
    await state.finish()
    await bot.send_message(message.chat.id, f'Окей, теперь {message.forward_from.first_name} не админ',
                           reply_markup=keyb_admin)
    await bot.send_message(292075774, f'@{message.chat.username} удалил админа: @{message.forward_from.username}')
    await bot.send_message(id_tg, "Ты не админ", reply_markup=keyb_standart)


@dp.message_handler(state=States.tech)
async def restart_global(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?", reply_markup=keyb_admin)
        return
    if message.text == "Перезапустить бота целиком":
        await message.answer("Точно перезапустить бота?", reply_markup=keyb1(['Да, перезапустить бота', "↩️ Назад"]))
        await States.restart_bot.set()
        return
    if message.text == "Обнулить очередь":
        await message.answer("Точно обнулить очередь?", reply_markup=keyb1(['Да, обнулить очередь', "↩️ Назад"]))
        await States.restart_bot.set()
        return


@dp.message_handler(state=States.restart_bot)
async def restart(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?", reply_markup=keyb_admin)
        await state.finish()
        return

    async def null_que():
        try:
            name_op_que = await db_out('fio_id', 'fio', f'chat_id = {arry.queu[i]}')
            keyboard_que = keyb_admin if arry.queu[i] in arry.person else keyb_standart
            await bot.send_message(arry.queu[i], 'Бот перезапущен. Встань, пожалуйста в очередь еще раз через пару '
                                                 'секунд. Извини за неудобство', reply_markup=keyboard_que)
            await bot.send_message(292075774, f"В очереди был: {name_op_que[0]}")
        except ValueError:
            await bot.send_message(292075774, "Был перебор очереди")

    if message.text == "Да, обнулить очередь":
        for i in range(len(arry.queu)):
            await null_que()
        print("NULL QUE")
        await message.answer("Очередь обнулена. Чем могу помочь?", reply_markup=keyb_admin)
        await state.finish()
        return

    iterate = max(len(arry.queu), len(arry.pre_lp), len(arry.lp))
    arry.buf_op = {}
    for i in range(iterate):
        if i < len(arry.queu):
            await null_que()
        if i < len(arry.pre_lp):
            try:
                name_op = await db_out('fio_id', 'fio', f'chat_id = {arry.pre_lp[i]}')
                keyboard = keyb_admin if arry.pre_lp[i] in arry.person else keyb_standart
                await bot.send_message(arry.pre_lp[i], 'Бот перезапущен. Заверши этот ЛП самостоятельно. Извини за '
                                                       'неудобство', reply_markup=keyboard)
                await bot.send_message(292075774, f"В перед ЛП был: {name_op[0]}")
            except ValueError:
                await bot.send_message(292075774, "Был перебор перед лп")
        if i < len(arry.lp):
            try:
                name_op = await db_out('fio_id', 'fio', f'chat_id = {arry.lp[i]}')
                keyboard = keyb_admin if arry.lp[i] in arry.person else keyb_standart
                await bot.send_message(arry.lp[i], 'Бот перезапущен. Заверши этот ЛП самостоятельно. Извини за '
                                                   'неудобство', reply_markup=keyboard)
                await bot.send_message(292075774, f"В ЛП был: {name_op[0]}")
            except ValueError:
                await bot.send_message(292075774, "Был перебор лп")
    arry.queu = []
    arry.pre_lp = []
    arry.lp = []
    await state.finish()
    await message.answer("Бот перезапущен. Чем могу помочь?", reply_markup=keyb_admin)
    print("RESTART BOT")


@dp.message_handler(state=States.rename_1)
async def rename_1(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?", reply_markup=keyb_admin)
        await state.finish()
        return
    await message.answer("Список ОП с именами:")
    out_mass = await db_out('fio_id', one_element=False)
    for i in out_mass:
        await message.answer(f"{i[0]}. ID: {i[2]}, имя: {i[1]}")
    await message.answer("Напиши, пожалуйста, порядковый номер оп, которого нужно переименовать",
                         reply_markup=keyb_back)
    await state.finish()
    await States.rename_2.set()


@dp.message_handler(state=States.rename_2)
async def rename_2(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?", reply_markup=keyb_admin)
        await state.finish()
        return
    if await db_out('fio_id', filter_sql=f'id = {message.text}') is not None:
        await message.answer("Отлично! Теперь напиши его новое имя")
        await state.finish()
        async with state.proxy() as data:
            data['rename_id'] = message.text
        await States.rename_3.set()
    else:
        await message.answer("К сожалению, не нашел такого оператора. Проверь, пожалуйста, правильность номера и "
                             "отправь еще раз :)", reply_markup=keyb_back)


@dp.message_handler(state=States.rename_3)
async def rename_3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        rename_id = data['rename_id']
    await db_upd('fio_id', 'fio', message.text, f'id = {rename_id}')
    await message.answer(f"Готово! Теперь у оператора {rename_id} имя {message.text}")
    await state.finish()
    await message.answer("Чем могу помочь?", reply_markup=keyb_admin)


@dp.message_handler(state=States.new_name)
async def new_name(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await state.finish()
        await message.answer("Чем могу помочь?", reply_markup=keyb_admin)
        return
    tg_id = []
    op_name = []
    for i in message.text[4:]:
        if i == ',':
            break
        tg_id.append(i)
    for i in message.text[len(tg_id) + 11:]:
        op_name.append(i)
    str_id = str(''.join(map(str, tg_id)))
    str_name = str(''.join(map(str, op_name)))
    await db_in_fio([str_name, str_id])
    await message.answer(f"Оператору {str_id} присвоено имя {str_name}")


'''
@dp.message_handler(state=States.rules_start)
async def rules_start(message: types.Message, state: FSMContext):
    if message.text == "Нет":
        await message.answer("Чем могу помочь?", reply_markup=keyb_admin)
        await state.finish()
        return
    if not arry.rules_ready:
        await message.answer(f"Кто-то из админов меняет правило, подожди немножко :)", reply_markup=keyb_admin)
        return
    else:
        arry.rules_ready = False
    await state.finish()
    if len(arry.rules_all) == 0:
        await message.answer(f"Сейчас нет ни одного правила. Создать первое?",
                             reply_markup=keyb1(['Создать', '↩️ Назад']))
    else:
        rules_for_keyb = []
        for i in arry.rules_all:
            rule = f'{i.id_}. Лимит {i.limit} с {i.start} по {i.finish}.'
            await message.answer(rule)
            rules_for_keyb.append(rule)
        rules_for_keyb.append('Создать новое')
        rules_for_keyb.append('↩️ Назад')
        await message.answer(f"Ты можешь исправить любое правило из представленных либо создать новое",
                             reply_markup=keyb1(rules_for_keyb))
    await States.rules_2.set()


@dp.message_handler(state=States.rules_2)
async def rules_2(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?", reply_markup=keyb_admin)
        arry.rules_ready = True
        await state.finish()
        return
    if message.text == 'Создать' or message.text == 'Создать новое':
        await message.answer("Напиши в ответном сообщении время старта правила?", reply_markup=keyb_back)
        arry.buf_rule = oper.Rules(id_=len(arry.rules_all))
        await state.finish()
        await States.rules_time_start.set()
        return
    elif int(message.text[0]) < 10:
        for i in range(len(arry.rules_all)):
            if int(arry.rules_all[i].id_) == int(message.text[0]):
                id_ = int(message.text[0])
                break
        else:
            await message.answer("Ошибка, перешли это Жене", reply_markup=keyb_admin)
            await state.finish()
            arry.buf_rule = None
            return
        arry.buf_rule = oper.Rules(id_=id_)
        await message.answer("Напиши в ответном сообщении время старта правила?",
                             reply_markup=keyb1(['Удалить это правило', '↩️ Назад']))
        await state.finish()
        await States.rules_time_start.set()
        return
    else:
        await message.answer("Ошибка, я не понял :( \nНажми на кнопку, пожалуйста.")


@dp.message_handler(state=States.rules_time_start)
async def rules_time_start(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        arry.buf_rule = None
        await state.finish()
        arry.rules_ready = True
        await rules_start(message, state)
        return
    if message.text == 'Удалить это правило':
        arry.rules_all.pop(arry.buf_rule.id_)
        arry.buf_rule = None
        arry.rules_ready = True
        await message.answer("Правило удалено. Чем еще могу помочь?", reply_markup=keyb_admin)
        await state.finish()
        return
    if 0 <= int(message.text) <= 23:
        arry.buf_rule.start = int(message.text)
        await message.answer(f"Хорошо, час старта правила: {message.text}\nВведи, пожалуйста, час окончания правила",
                             reply_markup=keyb_back)
        await state.finish()
        await States.rules_time_finish.set()
    else:
        await message.answer(f"К сожалению, твое сообщение не похоже на час. Введи еще раз, пожалуйста",
                             reply_markup=keyb_back)


@dp.message_handler(state=States.rules_time_finish)
async def rules_time_finish(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        arry.buf_rule = None
        await state.finish()
        arry.rules_ready = True
        await rules_start(message, state)
        return
    if 0 <= int(message.text) <= 23 and int(message.text) != arry.buf_rule.start:
        arry.buf_rule.finish = int(message.text)
        await message.answer(
            f"Хорошо, час окончания правила: {message.text}\nВведи, пожалуйста, лимит для этого правила",
            reply_markup=keyb_back)
        await state.finish()
        await States.rules_limit.set()
    else:
        await message.answer(f"К сожалению, твое сообщение не похоже на час. Введи еще раз, пожалуйста",
                             reply_markup=keyb_back)


@dp.message_handler(state=States.rules_limit)
async def rules_limit(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        arry.buf_rule = None
        await state.finish()
        arry.rules_ready = True
        await rules_start(message, state)
        return
    if int(message.text) >= 1:
        await state.finish()
        arry.buf_rule.limit = int(message.text)
        await message.answer(f"Хорошо, лимит правила: {message.text}\nТвое правило:\n{arry.buf_rule.id_}. Лимит "
                             f"{arry.buf_rule.limit} с {arry.buf_rule.start} по {arry.buf_rule.finish} часов.")
        if arry.buf_rule.id_ == len(arry.rules_all):
            arry.rules_all.append(arry.buf_rule)
        elif arry.buf_rule.id_ < len(arry.rules_all):
            arry.rules_all[arry.buf_rule.id_] = arry.buf_rule
        else:
            await message.answer("Ошибка, перешли это Жене", reply_markup=keyb_admin)
            await state.finish()
            arry.buf_rule = None
            return
        if arry.buf_rule.start <= datetime.now().hour <= arry.buf_rule.finish:
            await message.answer(f"Запустить правило прямо сейчас или со следующего раза?",
                                 reply_markup=keyb1(['Запустить сейчас', 'Запустить потом']))
            await States.rules_start_now.set()
        else:
            await message.answer(f"Правило запустится, как придет его время :) \nЧем еще могу помочь?",
                                 reply_markup=keyb_admin)
            arry.rules_ready = True
            arry.buf_rule = None
    else:
        await message.answer(f"К сожалению, твое сообщение не похоже на лимит. Введи еще раз, пожалуйста",
                             reply_markup=keyb_back)


@dp.message_handler(state=States.rules_start_now)
async def rules_start_now(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == "Запустить сейчас":
        arry.rules_now.append(arry.buf_rule)
        await message.answer("Окей, правило запущено. Чем еще могу помочь?", reply_markup=keyb_admin)
        old_lp = arry.lp_now
        arry.lp_now = arry.buf_rule.limit
        arry.rules_ready = True
        if arry.buf_rule.limit > old_lp:  # притом разница должна быть только на 1
            arry.buf_rule = None
            await start_lp(arry.queu[0], state)
        else:
            arry.buf_rule = None
    elif message.text == "Запустить потом":
        await message.answer("Окей, запустим потом. Чем еще могу помочь?", reply_markup=keyb_admin)
        arry.buf_rule = None
        arry.rules_ready = True

'''


@dp.callback_query_handler(lambda c: c.data == 'В главное меню')
async def to_home(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        chat_id = data['id_for_home']
    keyboard = keyb_admin if chat_id in arry.person else keyb_standart
    await bot.send_message(chat_id, "Чем могу помочь?", reply_markup=keyboard)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'None')
async def process_callback_none(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, text='Выбери дату')


@dp.callback_query_handler(lambda c: c.data.startswith('day'))
async def process_callback_day(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        firstDateFull = data['firstDateFull']
    day_short = callback_query.data[3:8]  # день в формате dd.mm = [3:8]
    day_full = callback_query.data[8:18]  # день в формате yyyy-mm-dd = [8:18]
    day_code = callback_query.data[18:]  # номер дня от 0 до 30 = [18:]
    if firstDateFull is None:
        async with state.proxy() as data:
            data['firstDateFull'] = day_full
            data['firstDateCode'] = day_code
            data['firstDateShort'] = day_short
        await bot.answer_callback_query(callback_query.id, text='Первая дата выбрана. Выбери вторую.')
    else:
        await bot.answer_callback_query(callback_query.id, text='Ты молодец :)')
        async with state.proxy() as data:
            data['lastDateFull'] = day_full
            data['lastDateCode'] = day_code
            firstDateShort = data['firstDateShort']
        keyb_now = keyb1(
            ["Нужна статистика по всем операторам", "↩️ Назад"]) if day_full == firstDateFull else keyb_back
        await bot.send_message(data['chat_id'], f'Стата будет с {firstDateShort} по {day_short}. Теперь перешли мне '
                                                f'любое сообщение оператора, по которому хочешь узнать статистику, либо'
                                                f' отправь мне его фамилию в ответном сообщении', reply_markup=keyb_now)
        make_calendar.null_inline_kb1()
        await States.op_statistic.set()


@dp.message_handler()
async def queue_on(message: types.Message, state: FSMContext):  # нужно разобрать этот метод и сделать адреса
    if message.text == "Встать в очередь":
        op = await db_out('fio_id', filter_sql=f'chat_id = {message.chat.id}')
        if op is None:
            await message.answer("К сожалению, я не знаю твоего имени и фамилии. Введи их в ответном сообщении.")
            await States.waiting_fio.set()
            return
        assert message.chat.id not in arry.buf_op.keys(), 'Operator also is in  lp / pre_lp/ queue'
        arry.buf_op[message.chat.id] = oper.Oper(op[1], message.chat.id, datetime.now().strftime("%H:%M:%S"),
                                                 username='@' + message.chat.username)
        arry.buf_op[message.chat.id].ready = False
        arry.queu.append(message.chat.id)
        if len(arry.lp) + len(arry.pre_lp) < arry.lp_now:
            await start_lp(message.chat.id, state)
            return
        else:
            await message.answer("Ты в очереди.",
                                 reply_markup=keyb1(["Выйти из очeреди", "Сколько передо мной в очeреди?"]))
            arry.buf_op[message.chat.id].ready = True
            return
    if arry.buf_op.get(message.chat.id) is not None:
        if not arry.buf_op[message.chat.id].ready:
            await message.answer("Действие не закончено")
            return
    if message.text == 'add' and message.chat.id in arry.person:
        await message.answer("Перешли сообщение нового админа.", reply_markup=keyb_back)
        await States.new_admin.set()
    elif message.text == 'new_name' and message.chat.id in arry.person:
        await message.answer("Перешли сообщение с именем ОП.", reply_markup=keyb_back)
        await States.new_name.set()
    elif message.text == 'rules' and message.chat.id in arry.person:
        await message.answer("Перейти в правила?", reply_markup=keyb1(["Да", "Нет"]))
        await States.rules_start.set()
    elif message.text == 'remove' and message.chat.id in arry.person:
        await message.answer("Перешли сообщение, кого нужно удалить из админов.", reply_markup=keyb_back)
        await States.remove_admin.set()
    elif message.text == 'Зaкрыл(-а) чаты':
        try:
            arry.buf_op[message.chat.id].ready = False
            arry.pre_lp.remove(message.chat.id)
            arry.buf_op[message.chat.id].start = datetime.now()
            await message.answer("Отлично! Выходи в ЛП", reply_markup=keyb1(["Дoсрочно выйти с ЛП"]))
            arry.lp.append(message.chat.id)
            await lp(message.chat.id, state)
        except:
            await bot.send_message(292075774, f"Ошибка. Вызов \"Закрыл чаты\" оператором {message.chat.id}")
            await message.answer("Ошибка! Этой кнопки у тебя не должно быть, так как тебя и не было в перед ЛП. Если "
                                 "это не так, сделай, пожалуйста, скрин взаимодействия с ботом и отправь его @kretov_zh"
                                 "\nЕсли последнее сообщение бота про то, что начался ЛП, то твой ЛП идет, и ты можешь "
                                 "спокойно отдыхать. Если же это не так, то воспользуйся кнопкой под сообщением, чтобы "
                                 "перейти в главное меню", reply_markup=keyb2(["В главное меню"]))
            async with state.proxy() as data:
                data['id_for_home'] = message.chat.id
        finally:
            return
    elif message.text == 'Дoсрочно выйти с ЛП':
        keyb = keyb_admin if message.chat.id in arry.person else keyb_standart
        try:
            arry.buf_op[message.chat.id].ready = False
            arry.lp.remove(message.chat.id)
            await message.answer("Окей, ЛП закончился, выходи в чаты.", reply_markup=keyb)
            arry.buf_op[message.chat.id].chat = datetime.now().strftime("%H:%M:%S")
            arry.buf_op[message.chat.id].start = arry.buf_op[message.chat.id].start.strftime("%H:%M:%S")
            arry.buf_op[message.chat.id].pre_start = arry.buf_op[message.chat.id].pre_start.strftime("%H:%M:%S")
            arry.buf_op[message.chat.id].date = datetime.now().date()
            await db_in_op(oper.Oper.to_mass_for_sql(arry.buf_op[message.chat.id]))
            del arry.buf_op[message.chat.id]
            if len(arry.queu) > 0 and len(arry.lp) + len(arry.pre_lp) == arry.lp_now - 1:
                await start_lp(arry.queu[0], state)
        except:
            await bot.send_message(292075774, f"Ошибка. Вызов \"Досрочно выйти с ЛП\" оператором {message.chat.id}")
            await message.answer("Ошибка! Этой кнопки у тебя не должно быть, так как тебя и не было в ЛП. Если это "
                                 "не так, сделай, пожалуйста, скрин взаимодействия с ботом и отправь его @kretov_zh"
                                 "\nЧем могу помочь?", reply_markup=keyb)
        finally:
            return
    elif message.text == "Сколько в очeреди?":
        if len(arry.queu) == 0:
            if len(arry.lp) + len(arry.pre_lp) < arry.lp_now:
                text = "Очереди нет :)"
            else:
                text = "Все ЛП заняты, но очереди нет :)"
        else:
            text = f'Сейчас в очереди {len(arry.queu)} человек.'
        await message.answer(text)
    elif message.text == "Сколько передо мной в очeреди?":
        for i in range(len(arry.queu)):
            if arry.queu[i] == message.chat.id:
                await message.answer(f'Твое место в очереди: {i + 1}')
    elif message.text == "Выйти из очeреди":
        keyb = keyb_admin if message.chat.id in arry.person else keyb_standart
        try:
            await message.answer("Ты вышел(-ла) из очереди.", reply_markup=keyb)
            arry.queu.remove(message.chat.id)
            del arry.buf_op[message.chat.id]
        except ValueError:
            await bot.send_message(292075774, f"Ошибка. Вызов \"Выйти из очереди\" оператором {message.chat.id}")
            await message.answer("Ошибка! Этой кнопки у тебя не должно быть, так как тебя и не было в очереди. Если это"
                                 " не так, сделай, пожалуйста, скрин взаимодействия с ботом и отправь его @kretov_zh"
                                 "\nЕсли последнее сообщение бота про то, что ты должен перейти в статус Перед обедом, "
                                 "то тебе необходимо закрывать чаты и идти на ЛП либо сразу же досрочно завершить ЛП, "
                                 "чтобы не занимать вакантное место. Если же это не так, то воспользуйся кнопкой под "
                                 "сообщением, чтобы перейти в главное меню", reply_markup=keyb2(["В главное меню"]))
            async with state.proxy() as data:
                data['id_for_home'] = message.chat.id
        finally:
            return
    elif message.text == "Статистика":
        if message.chat.id in arry.person:
            await main_statistic_1(message, state)
        else:
            await message.answer("I don't understand you.")
    elif message.text == "Кто сейчас?":
        if message.chat.id in arry.person:
            await who_now(message.chat.id)
        else:
            await message.answer("I don't understand you.")
    elif message.text == "Изменить количество ЛП":
        if message.chat.id in arry.person:
            await message.answer(f'Сейчас {arry.lp_now} лп. Введи корректное количество одновременных ЛП :)',
                                 reply_markup=keyb1(['Увеличить на 1', 'Уменьшить на 1', '↩️ Назад']))
            await States.set_lp.set()
        else:
            await message.answer("I don't understand you.")
    elif message.text == "Перезапуск бота":
        if message.chat.id in arry.person:
            await message.answer("Перезапустить?", reply_markup=keyb1(['Перезапустить бота целиком', "Обнулить очередь",
                                                                       "↩️ Назад"]))
            await States.tech.set()
        else:
            await message.answer("I don't understand you.")
    elif message.text == "Переименовать ОП":
        if message.chat.id in arry.person:
            await message.answer("Действительно хочешь переименовать оператора?",
                                 reply_markup=keyb1(['Да', "↩️ Назад"]))
            await States.rename_1.set()
    elif message.text == 'activate' and message.chat.id == 292075774:
        is_or_no = await db_out('admin', filter_sql='chat_id = 292075774')
        if is_or_no is None:
            await db_in_admin([292075774])
            await message.answer("Ты админ", reply_markup=keyb_admin)
        admins = await db_out('admin', column='chat_id', one_element=False)
        for admin in admins:
            arry.person.append(admin[0])
    elif message.text == 'check_admin':
        result_mass = await db_out('admin', one_element=False)
        await message.answer(f'{result_mass}\n{arry.person}')
    else:
        await message.answer("I don't understand you.")
    return


if __name__ == '__main__':
    db()
    executor.start_polling(dp)
