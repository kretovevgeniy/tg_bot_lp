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
from keyb import keyb1, keyb_standart, keyb_admin, keyb_back

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


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if str(message.chat.id) in arry.que_name_id.keys():
        print(f"попытка start. ID {message.chat.id}")
        return
    await message.answer(f'Привет, {message.from_user.first_name}! Это бот по ЛП. Напиши, пожалуйста одним сообщением '
                         f'свою реальную фамилию и реальное имя.', reply_markup=types.ReplyKeyboardRemove())
    await States.waiting_fio.set()


@dp.message_handler(state=States.waiting_fio)
async def set_fio(message: types.Message, state: FSMContext):
    name = message.text
    arry.que_name_id[str(message.chat.id)] = name
    keyb = keyb_admin if message.chat.id in arry.person else keyb_standart
    await message.answer(f'Приятно познакомиться, {name} :)\nТеперь ты можешь пользоваться моим функционалом.',
                         reply_markup=keyb)
    await state.finish()


def day_stat():
    arry.day_oper[6] = arry.day_oper[5].copy()
    arry.day_oper[5] = arry.day_oper[4].copy()
    arry.day_oper[4] = arry.day_oper[3].copy()
    arry.day_oper[3] = arry.day_oper[2].copy()
    arry.day_oper[2] = arry.day_oper[1].copy()
    arry.day_oper[1] = arry.day_oper[0].copy()
    arry.day_oper[0].clear()
    return


@dp.message_handler(state=States.main_statistic)
async def main_statistic_1(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?",
                             reply_markup=keyb_admin)
        await state.finish()
        return
    i = 0
    if message.text == 'Сегодня':
        i = 0
    elif message.text == 'Вчера':
        i = 1
    elif message.text == '2 дня назад':
        i = 2
    elif message.text == '3 дня назад':
        i = 3
    elif message.text == '4 дня назад':
        i = 4
    elif message.text == '5 дней назад':
        i = 5
    elif message.text == '6 дней назад':
        i = 6
    if len(arry.day_oper[i]) == 0:
        await message.answer("Пусто :(", reply_markup=keyb_admin)
        await state.finish()
        return
    await message.answer("Теперь перешли мне любое сообщение оператора, по которому хочешь узнать статистику, либо "
                         "отправь мне его фамилию в ответном сообщении",
                         reply_markup=keyb1(["Нужна статистика по всем операторам", "↩️ Назад"]))
    arry.i = i
    await state.finish()
    await States.op_statistic.set()


@dp.message_handler(state=States.op_statistic)
async def main_statistic_2(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Чем могу помочь?",
                             reply_markup=keyb_admin)
        await state.finish()
        return

    async def send(i):
        text = f'ФИО: {i.fio} \nДата: {i.date}\nВстал в очередь в {i.que} \nВышел в перед обедом в {i.pre_start} ' \
               f'\nВышел в ЛП в {i.start} \nВернулся в чаты в {i.chat} \nUsername: {i.username}'
        await message.answer(text)

    async def send_2():
        await message.answer("Чем еще могу помочь? :)", reply_markup=keyb_admin)

    j = arry.i
    id = 0
    fio = "None"
    if message.text == "Нужна статистика по всем операторам":
        id = 0
    elif message.forward_date is not None:
        try:
            id = message.forward_from.id
        except:
            await message.answer("Не получается определить ID аккаунта. Скорее всего, настройки приватности оператора "
                                 "не позволяют выяснить его ID. Попроси, пожалуйста, оператора внести этого бота в "
                                 "исключения в разделе \"Настройки\" -> \"Конфиденциальность\" -> \"Пересылка "
                                 "сообщений\"", reply_markup=keyb_admin)
            await state.finish()
            return
    else:
        fio = message.text.lower()
    if id == 0 and fio == "None":
        for i in arry.day_oper[j]:
            await send(i)
        await send_2()
    elif id != 0:
        for i in arry.day_oper[j]:
            if i.chat_id == id:
                await send(i)
        await send_2()
    elif fio != "None":
        for i in arry.day_oper[j]:
            if fio in i.fio.lower():
                await send(i)
        await send_2()
    await state.finish()


async def pre_lp(chat_id):
    arry.buf_op[chat_id].ready = True
    await asyncio.sleep(100)
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
            print('обработка исключения pre_lp')


async def lp(chat_id, state: FSMContext):
    arry.buf_op[chat_id].ready = True
    await asyncio.sleep(20)
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
                if len(arry.day_oper[0]) > 0:
                    if arry.day_oper[0][0].date != datetime.now().date():
                        day_stat()
                arry.day_oper[0].append(arry.buf_op[chat_id])
                del arry.buf_op[chat_id]
                if len(arry.queu) > 0 and len(arry.lp) + len(arry.pre_lp) == arry.lp_now - 1:
                    await start_lp(arry.queu[0], state)
            break
        except NetworkError:
            await asyncio.sleep(5)
            print('обработка исключения lp')


async def start_lp(chat_id, state: FSMContext):
    arry.buf_op[chat_id].pre_start = datetime.now()         #.strftime("%H:%M:%S")
    text = "Оказывается, очередь как раз скоро подойдет! Выходи в \"перед обедом\"и закрывай чаты :)"
    await bot.send_message(chat_id, text, reply_markup=keyb1(["Зaкрыл(-а) чаты"]))
    arry.queu.remove(chat_id)
    arry.pre_lp.append(chat_id)
    await pre_lp(chat_id)
    if chat_id in arry.pre_lp:
        arry.pre_lp.remove(chat_id)
        arry.lp.append(chat_id)
        await lp(chat_id, state)


async def who_now(chat_id):
    lp = arry.lp
    pre_lp = arry.pre_lp
    qu = arry.queu
    if len(lp) > 0:
        lp_text = ""
        for i in range(len(lp)):
            a = datetime.now() - arry.buf_op[lp[i]].start
            lp_text += f'\n{arry.buf_op[lp[i]].fio} {timedelta(seconds=int(a.total_seconds()))}'
        lp_text1 = f'В ЛП: {lp_text}'
    else:
        lp_text1 = 'В ЛП никого'
    await bot.send_message(chat_id, lp_text1)
    if len(pre_lp) > 0:
        pre_lp_text = ""
        for i in range(len(pre_lp)):
            a = datetime.now() - arry.buf_op[pre_lp[i]].pre_start
            pre_lp_text += f'\n{arry.buf_op[pre_lp[i]].fio} {timedelta(seconds=int(a.total_seconds()))}'
        pre_lp_text1 = f'В перед обедом: {pre_lp_text}'
    else:
        pre_lp_text1 = "В перед обедом никого"
    await bot.send_message(chat_id, pre_lp_text1)
    if len(qu) > 0:
        qu_text = ""
        for i in range(len(qu)):
            qu_text += f'\n{arry.buf_op[qu[i]].fio} с {arry.buf_op[qu[i]].que}'
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
    old_lp = arry.lp_now
    await state.finish()
    if message.text == "Увеличить на 1":
        arry.lp_now += 1
        await message.answer(f'Количество одновременных ЛП изменилось. Новое значение: {arry.lp_now}',
                             reply_markup=keyb_admin)
        arry.day_oper[0].append(oper.Oper(f'@{message.chat.username}', 0, old_lp, arry.lp_now,
                                          datetime.now().strftime("%H:%M:%S"), date=datetime.now().date()))
        await start_lp(arry.queu[0], state)
    elif message.text == 'Уменьшить на 1':
        arry.lp_now -= 1
        await message.answer(f'Количество одновременных ЛП изменилось. Новое значение: {arry.lp_now}',
                             reply_markup=keyb_admin)
        arry.day_oper[0].append(oper.Oper(f'@{message.chat.username}', 0, old_lp, arry.lp_now,
                                          datetime.now().strftime("%H:%M:%S"), date=datetime.now().date()))


@dp.message_handler(state=States.new_admin)
async def test(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?",
                             reply_markup=keyb_admin)
        await state.finish()
        return
    try:
        id = message.forward_from.id
    except:
        await message.answer("Не получается определить ID аккаунта. Скорее всего, настройки приватности оператора "
                             "не позволяют выяснить его ID. Попроси, пожалуйста, оператора внести этого бота в "
                             "исключения в разделе \"Настройки\" -> \"Конфиденциальность\" -> \"Пересылка "
                             "сообщений\"", reply_markup=keyb_admin)
        await state.finish()
        return
    arry.person.append(id)
    await message.answer(f'Окей, теперь {message.forward_from.first_name} админ',
                         reply_markup=keyb_admin)
    await bot.send_message(292075774,
                           f'@{message.chat.username} добавил нового админа: @{message.forward_from.username}')
    await bot.send_message(id, "Ты админ", reply_markup=keyb_admin)
    await state.finish()


@dp.message_handler(state=States.remove_admin)
async def test2(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?",
                             reply_markup=keyb_admin)
        await state.finish()
        return
    try:
        id = message.forward_from.id
    except:
        await message.answer("Не получается определить ID аккаунта. Скорее всего, настройки приватности оператора "
                             "не позволяют выяснить его ID. Попроси, пожалуйста, оператора внести этого бота в "
                             "исключения в разделе \"Настройки\" -> \"Конфиденциальность\" -> \"Пересылка "
                             "сообщений\"", reply_markup=keyb_admin)
        await state.finish()
        return
    if id not in arry.person:
        await state.finish()
        return
    arry.person.remove(id)
    await state.finish()
    await bot.send_message(message.chat.id, f'Окей, теперь {message.forward_from.first_name} не админ',
                           reply_markup=keyb_admin)
    await bot.send_message(292075774, f'@{message.chat.username} удалил админа: @{message.forward_from.username}')
    await bot.send_message(id, "Ты не админ", reply_markup=keyb_standart)


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
            keyb = keyb_admin if arry.queu[i] in arry.person else keyb_standart
            await bot.send_message(arry.queu[i], 'Бот перезапущен. Встань, пожалуйста в очередь еще раз. Извини за '
                                                 'неудобство', reply_markup=keyb)
            print(f"В очереди был: {arry.que_name_id[str(arry.queu[i])]}")
        except ValueError:
            print("Был перебор")

    if message.text == "Да, обнулить очередь":
        for i in range(len(arry.queu)):
            await null_que()
        print("NULL QUE")
        await message.answer("Очередь обнулена. Чем могу помочь?", reply_markup=keyb_admin)
        await state.finish()
        return

    iter = max(len(arry.queu), len(arry.pre_lp), len(arry.lp))
    arry.buf_op = {}
    for i in range(iter):
        if i < len(arry.queu):
            await null_que()
        if i < len(arry.pre_lp):
            try:
                keyb = keyb_admin if arry.pre_lp[i] in arry.person else keyb_standart
                await bot.send_message(arry.pre_lp[i], 'Бот перезапущен. Заверши этот ЛП самостоятельно. Извини за '
                                                       'неудобство', reply_markup=keyb)
                print(f"В перед ЛП был: {arry.que_name_id[str(arry.pre_lp[i])]}")
            except ValueError:
                print("Был перебор")
        if i < len(arry.lp):
            try:
                keyb = keyb_admin if arry.lp[i] in arry.person else keyb_standart
                await bot.send_message(arry.lp[i], 'Бот перезапущен. Встань, пожалуйста в очередь еще раз. Извини за '
                                                   'неудобство', reply_markup=keyb)
                print(f"В ЛП был: {arry.que_name_id[str(arry.lp[i])]}")
            except ValueError:
                print("Был перебор")
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
    for i in arry.que_name_id:
        await message.answer(f"\nID: {i}, имя: {arry.que_name_id[i]}")
    await message.answer("Напиши, пожалуйста, ID оп, которого нужно переименовать", reply_markup=keyb_back)
    await state.finish()
    await States.rename_2.set()


@dp.message_handler(state=States.rename_2)
async def rename_2(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await message.answer("Чем могу помочь?", reply_markup=keyb_admin)
        await state.finish()
        return
    if str(message.text) in arry.que_name_id.keys():
        arry.rename_id = message.text
        await message.answer("Отлично! Теперь напиши его новое имя")
        await state.finish()
        await States.rename_3.set()
    else:
        await message.answer("К сожалению, не нашел такого оператора. Проверь, пожалуйста, правильность ID и отправь "
                             "еще раз :)", reply_markup=keyb_back)


@dp.message_handler(state=States.rename_3)
async def rename_3(message: types.Message, state: FSMContext):
    arry.que_name_id[arry.rename_id] = message.text
    await message.answer(f"Готово! Теперь у оператора {arry.rename_id} имя {message.text}")
    arry.rename_id = 0
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
    arry.que_name_id[str_id] = str_name
    print(arry.que_name_id)
    await message.answer(f"Оператору {str_id} присвоено имя {str_name}")


async def rules(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await state.finish()
        await message.answer("Чем могу помочь?", reply_markup=keyb_admin)
        return
    if len(arry.rules_now) == 0 and len(arry.rules_done) == 0 and len(arry.rules_undone) == 0:
        await message.answer(f"Сейчас нет ни одного правила. Создать первое?",
                             reply_markup=keyb1(['Создать', '↩️ Назад']))
    else:
        for i in arry.rules_all:
            await message.answer(i)
        rules_for_keyb = arry.rules_all
        rules_for_keyb.append('↩️ Назад')
        await message.answer(f"Ты можешь исправить любое правило из представленных либо создать новое",
                             reply_markup=keyb1(arry.rules_all))





@dp.message_handler()
async def queue_on(message: types.Message, state: FSMContext):  # нужно разобрать этот метод и сделать адреса
    if message.text == "Встать в очередь":
        if arry.que_name_id.get(str(message.chat.id)) is None:
            await message.answer("К сожалению, я не знаю твоего имени и фамилии. Введи их в ответном сообщении.")
            await States.waiting_fio.set()
            return
        print(arry.buf_op.keys())
        print(message.chat.id)
        assert message.chat.id not in arry.buf_op.keys()
        arry.buf_op[message.chat.id] = oper.Oper(arry.que_name_id[str(message.chat.id)], message.chat.id,
                                                 datetime.now().strftime("%H:%M:%S"),
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
            print(f"Ошибка. Вызов \"Закрыл чаты\" оператором {message.chat.id}")
            keyb = keyb_admin if message.chat.id in arry.person else keyb_standart
            await message.answer("Ошибка! Этой кнопки у тебя не должно быть, так как тебя и не было в перед ЛП. Если "
                                 "это не так, сделай, пожалуйста, скрин взаимодействия с ботом и отправь его @kretov_zh"
                                 "\nЧем могу помочь?", reply_markup=keyb)
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
            if len(arry.day_oper[0]) >= 1:
                if arry.day_oper[0][0].date != datetime.now().date():
                    day_stat()
            arry.day_oper[0].append(arry.buf_op[message.chat.id])
            del arry.buf_op[message.chat.id]
            if len(arry.queu) > 0 and len(arry.lp) + len(arry.pre_lp) == arry.lp_now - 1:
                await start_lp(arry.queu[0], state)
        except:
            print(f"Ошибка. Вызов \"Досрочно выйти с ЛП\" оператором {message.chat.id}")
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
            print(f"Ошибка. Вызов \"Выйти из очереди\" оператором {message.chat.id}")
            await message.answer("Ошибка! Этой кнопки у тебя не должно быть, так как тебя и не было в очереди. Если это"
                                 " не так, сделай, пожалуйста, скрин взаимодействия с ботом и отправь его @kretov_zh "
                                 "\nЧем могу помочь?", reply_markup=keyb)
        finally:
            return
    elif message.text == "Статистика":
        if message.chat.id in arry.person:
            await message.answer('За какой день нужна статистика?',
                                 reply_markup=keyb1(['Сегодня', 'Вчера', '2 дня назад', '3 дня назад', '4 дня назад',
                                                     '5 дней назад', '6 дней назад', "↩️ Назад"]))
            await States.main_statistic.set()
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
    else:
        await message.answer("I don't understand you.")
    return


if __name__ == '__main__':
    executor.start_polling(dp)
