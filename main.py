from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile, ChatMember
from aiogram.utils.markdown import hcode, hbold, hitalic
from aiogram.utils.exceptions import TelegramAPIError

from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.deep_linking import decode_payload

import pymysql
from pymysql import cursors
from datetime import datetime

import texts
import config


API_TOKEN = config.API_TOKEN_MAIN

db_host = config.db_host
db_user = config.db_user
db_database = config.db_database
db_port = config.db_port
db_password = config.db_password


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


full_date_time = ''
def timestamp():
    global full_date_time

    import dict
    months_dictionary = dict.months_dict

    now = datetime.now()
    date = now.strftime("%d.%m.%Y")
    time = now.strftime("%H:%M")

    day = (date.split('.'))[0]
    month = months_dictionary[(date.split('.'))[1]]
    year = (date.split('.'))[2]
    full_date_time = f'{day} {month} {year} - {time}'

async def check_access(user_id):
    if user_id != 1251526792:
        connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database,cursorclass=cursors.DictCursor)
        cursor = connection.cursor()

        cursor.execute(f'select ID from Data where user_id={user_id}')
        y = cursor.fetchone()
        connection.commit()

        if y is not None:
            cursor.execute(f'select access from Data where user_id={user_id}')
            access = cursor.fetchone()
            connection.commit()
            cursor.close()
            connection.close()

            access = access['access']
            return access
        else:
            return ''
    else:
        return 1


async def getstats(player_user_id):
    connection = pymysql.connect(host=config.db_host, port=config.db_port, user=config.db_user, password=config.db_password, database=config.db_database,cursorclass=cursors.DictCursor)
    cursor = connection.cursor()

    import dict
    level_dictionary = dict.level_dict

    waited_airdrop_text = ''
    all_icons_text = ''

    cursor.execute(f'select * from Data where user_id={player_user_id}')
    stats = cursor.fetchone()
    connection.commit()

    connection.close()

    frens_list_db = stats['referrals']
    waited_airdrop_db = stats['waited_airdrop']
    level_db = stats['level']
    all_skins_counter_db = stats['all_skins_counter']
    alltime_tokens = stats['alltime_tokens']
    alltime_conditions = stats['alltime_conditions']
    alltime_taps = stats['alltime_taps']


    frens_list = []
    if frens_list_db != '':
        frens_list_without_re = frens_list_db.split(',')
        for ex in frens_list_without_re:
            frens_list.append(ex)
        len_frens_list = len(frens_list)
    else:
        len_frens_list = 0

    if waited_airdrop_db == 0:
        waited_airdrop_text = 'Не дождались'
    elif waited_airdrop_db == 1:
        waited_airdrop_text = 'Дождались'

    level_value = level_dictionary[level_db]
    level_num = level_db

    if all_skins_counter_db != 30:
        all_icons_text = 'Вы не получили все скины'
    elif all_skins_counter_db == 30:
        all_icons_text = 'Вы получили все скины!'

    result = f'''{hbold("За все время накоплено")} — {hitalic(f"{alltime_tokens} Очков FIC")}\n\n{hbold("За все время получено")} — {hitalic(f"{alltime_conditions} Кондиций")}\n\n{hbold("За все время тапнуто")} — {hitalic(f"{alltime_taps} раз")}\n\n{hitalic(f"{all_icons_text}")}\n\n{hbold("Всего приглашено в игру")} — {hitalic(f"{len_frens_list} друзей")}\n\n{hbold("Ваш игровой уровень")} — {hitalic(f"#{level_num} {level_value}")}\n\n{hbold("Дождались AirDrop")} — {hitalic(f"{waited_airdrop_text}")}'''

    return result

async def add_user(user_id, username, fullname):
    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database,cursorclass=cursors.DictCursor)
    cursor = connection.cursor()

    try:
        lst_access = []
        cursor.execute(f'select access from Data')
        x = cursor.fetchall()
        connection.commit()

        for access_db_lst in x:
            lst_access.append(access_db_lst['access'])

        if 3 not in lst_access:
            lst = []
            cursor.execute('select user_id from Data')
            prof = cursor.fetchall()
            connection.commit()
            for e in prof:
                lst.append(e['user_id'])

            if user_id not in lst:
                # if int(user_id) == 187110373:
                #     await bot.send_message(chat_id=1251526792, text=f'{hbold("ТРЕВОГА!!!")}\n\nИВАННИКОВ ЗАРЕГИСТРИРОВАЛСЯ В БОТЕ ТОЛЬКО ЧТО!\n\n/off_app ДЛЯ ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ, {hitalic("ЛИБО ЖМИ НА КНОПКУ НИЖЕ.")}\nВЫБОР ЗА ТОБОЙ!', protect_content=True, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text="Уже нечего терять", callback_data="understood")), parse_mode='HTML')
                #     access_value = 0
                # else:
                await bot.send_message(chat_id=1251526792,text=f'{hbold("В боте @FigmentInterplanetaryCoin_bot только что зарегистрировался новый пользователь!")}\nUser_ID: <code>{int(user_id)}</code>',protect_content=True,reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text="Удалить",callback_data="understood")), parse_mode='HTML')
                access_value = 1

                referral_link = await get_start_link(f'{str(user_id)}', encode=True)
                cursor.execute('insert into Data(user_id, username_tg, referral_link, access) values({}, "{}", "{}", {})'.format(user_id, f"@{username}", referral_link, access_value))
                connection.commit()
                print(f'User {user_id}:@{username} added to Data table')
                return True
            else:
                return True
        elif 3 in lst_access:
            return False

    except Exception as ex:
        print(f"Error adding user {user_id}:@{username} to Data table: {ex}")
        return False

    connection.close()

def get_referral_link(user_id):
    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database,cursorclass=cursors.DictCursor)
    cursor = connection.cursor()

    try:
        cursor.execute(f"select referral_link from Data where user_id = {user_id}")
        result = cursor.fetchone()
        connection.commit()
        connection.close()

        if result:
            return result['referral_link']
        else:
            return None

    except Exception as ex:
        print(f"Error getting referral link for user {user_id}: {ex}")
        return None


def generate_referral_link(user_id):
    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database,cursorclass=cursors.DictCursor)
    cursor = connection.cursor()

    try:
        unique_link = f"https://t.me/FigmentInterplanetaryCoin_bot?start={user_id}"
        cursor.execute(f"update Data set referral_link = '{unique_link}' where user_id = {user_id}")
        connection.commit()
        connection.close()

        return unique_link

    except Exception as ex:
        print(f"Error generating referral link for user {user_id}: {ex}")
        return None


async def is_referral(message):
    try:
        if message.text.startswith('/start'):
            parts = message.text.split(' ')
            if len(parts) > 1:
                try:
                    referral_id_test = message.get_args()
                    referral_id = decode_payload(referral_id_test)
                    return referral_id
                except ValueError:
                    print(f"Error: Invalid referral ID: {parts[1]}")
                    return None
            else:
                return None
        else:
            return None
    except (IndexError, ValueError) as ex:
        print(f"Error checking referral status: {ex}")
        return None


async def add_referral(user_id, referral_id, usrnme, referral_username):
    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database,cursorclass=cursors.DictCursor)
    cursor = connection.cursor()
    try:
        if referral_id is not None:
            lst = []
            lst2 = []
            cursor.execute(f'select referrals from Data where user_id={user_id}')
            prof = cursor.fetchone()
            prof = prof['referrals']
            connection.commit()

            cursor.execute(f'select was_added_as_fren from Data where user_id={referral_id}')
            noob = cursor.fetchone()
            connection.commit()

            noob = noob['was_added_as_fren']

            result = prof.split(',')
            try:
                for u in result:
                    lst.append(int(u))
            except ValueError:
                pass

            if int(referral_id) != int(user_id):
                # handlers
                if referral_id not in lst:
                    if noob == 0:
                        if str(referral_id) in lst2:
                            pass
                            # i am forget why we are needing in this IF...
                        else:
                            if len(lst) <= 4:
                                print(f"Adding referral: user_id={user_id}, referral_id={referral_id}")
                                if prof != '':
                                    cursor.execute(f"update Data set referrals = CONCAT(referrals, ',', {referral_id}) where user_id = {user_id}")
                                else:
                                    cursor.execute(f"update Data set referrals = '{referral_id}' where user_id = {user_id}")
                                    print(f"Referral {referral_id} added to user {user_id} referrals")
                                timestamp()
                                connection.commit()
                                cursor.execute(f'''update Data set was_added_as_fren=1, was_added_as_fren_datetime='{full_date_time}' where user_id={referral_id}''')
                                connection.commit()
                                # cursor.execute(f'update Data set skin_11=1 where user_id={user_id}')
                                # connection.commit()
                                # cursor.execute(f'update Data set skin_11=1 where user_id={referral_id}')
                                # connection.commit()

                                await bot.send_message(
                                    chat_id=user_id,
                                    text=f"Йоу, {referral_username}!\n@{usrnme} Перешел по твоей ссылке и стал твоим другом!\n\nТы сможешь забрать свой подарок, когда твой друг зарегистрируется в приложении FIC App!",
                                    protect_content=True,
                                    reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text='Удалить', callback_data='understood'))
                                )
                            else:
                                cursor.execute(f'update Data set was_added_as_fren=2 where user_id={referral_id}')
                                connection.commit()
                                # If own has 5 frens

                    elif noob == 1:
                        pass
                        # This guy was added as fren to another player
                    elif noob == 2:
                        pass
                        # Guy was started this bot without link with referral id
            else:
                pass
                # Are u kidin' me? U try to add urself to ur referrals

    except Exception as ex:
        print(f"Error adding referral {referral_id} to user {user_id} referrals: {ex}")
        # Kinda logger if we haven't same handlers

    connection.close()


async def get_username(chat_id, user_id):
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    username = chat_member.user.first_name
    return username


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    acs = await check_access(message.chat.id)
    if acs == 0:
        await message.answer(text=texts.was_blocked_text, protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text="Понятно", callback_data="understood")))
    elif acs == 3:
        await message.answer(text=texts.tech_works_now_text, protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text="Понятно", callback_data="understood")))
    else:
        connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database, cursorclass=cursors.DictCursor)
        cursor = connection.cursor()

        x = await add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
        if (x is False) and (message.chat.id != 1251526792):
            await message.answer(text=texts.tech_works_now_text, protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text="Понятно", callback_data="understood")))
        elif x is True:
            referral_id = await is_referral(message)
            if referral_id is not None:
                ref_usrnme = await get_username(referral_id, referral_id)
                await add_referral(user_id=referral_id, referral_id=message.chat.id, referral_username=ref_usrnme, usrnme=message.from_user.username)
                await bot.send_photo(
                    photo=InputFile(r'Resources/Images/FIC Logo Strong.png'),
                    chat_id=message.chat.id,
                    caption=texts.start_text,
                    reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                        types.InlineKeyboardButton(text="FIC Меню", callback_data="fic_menu"),
                        types.InlineKeyboardButton(text="Получить FIC App", callback_data="download")
                    ),
                    protect_content=True,
                    parse_mode='HTML'
                )
            else:
                await bot.send_photo(
                    photo=InputFile(r'Resources/Images/FIC Logo Strong.png'),
                    chat_id=message.chat.id,
                    caption=texts.start_text,
                    reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                        types.InlineKeyboardButton(text="FIC Меню", callback_data="fic_menu"),
                        types.InlineKeyboardButton(text="Получить FIC App", callback_data="download")
                    ),
                    protect_content=True,
                    parse_mode='HTML'
                )
                cursor.execute(f'update Data set was_added_as_fren=2 where user_id={message.from_user.id}')
                connection.commit()

            connection.close()

@dp.message_handler(commands='help')
async def help_handler(message: types.Message):
    await bot.send_photo(
        photo=InputFile(r'Resources/Images/FIC Logo Strong.png'),
        chat_id=message.chat.id,
        caption=texts.help_text,
        reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton(text="Правила", callback_data="rules-list"),
            types.InlineKeyboardButton(text="Пользование", callback_data="h2u-list"),
            types.InlineKeyboardButton(text="Как играть?", callback_data="guide-list")
        ),
        protect_content=True,
        parse_mode='HTML'
    )

@dp.message_handler(content_types=["document"])
async def sticker_file_id(message: types.Message):
    if message.chat.id in [1251526792]:
        await message.answer(f"ID документа {message.document.file_id}")

@dp.message_handler(commands=['show', 'set', 'set_access', 'off_app', 'on_app', 'players', 'notify', 'test'])
async def command_handler(message: types.Message):
    if message.chat.id in [1251526792]:
        command = message.text.split()[0][1:]

        if command == 'show':
            try:
                access_command = 0
                args = message.text.split()[1:]
                if len(args) != 3:
                    await message.reply(
                        f'''{hbold("Неправильное количество аргументов для /show")}!\n\nИспользуйте:\n{hitalic("/show (таблица) (колонка) (идентификатор)")}''',
                        protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    return

                table = args[0]
                column = args[1]
                value = args[2]

                if len(value) <= 20:
                    if int(value) == 1251526792 and message.chat.id != 1251526792:
                        await message.reply(f'''{hbold("У этого пользователя нельзя просматривать данные!")}, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood"))''',
                                            protect_content=True, parse_mode='HTML')
                    elif int(value) == 1251526792 and message.chat.id == 1251526792:
                        access_command = 1

                elif len(value) >= 20:
                    if str(value) == '8934346:bLVRDGpadRCgCBf5sS1crWEm4bpgT2BTkAq9biZR' and message.chat.id != 1251526792:
                        await message.reply(f'''{hbold("У этого пользователя нельзя просматривать данные!")}, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood"))''',
                                            protect_content=True, parse_mode='HTML')
                    elif str(value) == '8934346:bLVRDGpadRCgCBf5sS1crWEm4bpgT2BTkAq9biZR' and message.chat.id == 1251526792:
                        access_command = 1

                if access_command == 1:
                    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,database=db_database, cursorclass=cursors.DictCursor)
                    cursor = connection.cursor()

                    if len(value) >= 20:
                        value_type = 'fic_id'
                        data_type = '"'
                    else:
                        value_type = 'user_id'
                        data_type = ""

                    if column != 'all':
                        cursor.execute(f"select {column} from {table} where {value_type}={data_type}{value}{data_type}")
                        select = cursor.fetchone()
                        select = select[f'{column}']
                        connection.commit()
                        cursor.close()
                        connection.close()

                        if column == 'fic_id' or column == 'user_id':
                            protect_content_value = False
                            hcode_start = '''<code>'''
                            hcode_end = '''</code>'''
                        else:
                            protect_content_value = True
                            hcode_start = ''
                            hcode_end = ''

                        await message.reply(
                            f'''{hbold(f"Вот полученные данные игрока с {value_type} {value} из таблицы {table}")}:\n\n<b>{column}</b>:\n{hcode_start}{select}{hcode_end}''',
                            protect_content=protect_content_value, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

                    elif column == 'all':
                        text = ''
                        cursor.execute(f"select * from {table} where {value_type}={data_type}{value}{data_type}")
                        select = cursor.fetchone()
                        connection.commit()
                        cursor.close()
                        connection.close()

                        for ex in select:
                            text += f'{ex} — {select[ex]}' + '\n'

                        await message.reply(
                            f'''{hbold(f"Вот все данные игрока с {value_type} {value}")} из таблицы {table}:\n\n{text}''',
                            protect_content=False, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    access_command = 0

            except Exception as e:
                await message.reply(f"Ошибка при выполнении /show:\n\n{e}", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

        elif command == 'set':
            try:
                access_command = 0
                args = message.text.split()[1:]
                if len(args) != 4:
                    await message.reply(
                        f'''{hbold("Неправильное количество аргументов для /set")}!\n\nИспользуйте:\n{hitalic("/set (таблица) (колонка) (новое значение) (идентификатор)")}''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    return
                table = args[0]
                column = args[1]
                new_value = args[2]
                user_id = args[3]

                if len(user_id) <= 20:
                    if int(user_id) == 1251526792 and message.chat.id != 1251526792:
                        await message.reply(f'''{hbold("У этого пользователя нельзя просматривать данные!")}''',
                                            protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    elif int(user_id) == 1251526792 and message.chat.id == 1251526792:
                        access_command = 1
                    elif int(user_id) != 1251526792 and message.chat.id == 1251526792:
                        access_command = 1

                elif len(user_id) >= 20:
                    if str(user_id) == '8934346:bLVRDGpadRCgCBf5sS1crWEm4bpgT2BTkAq9biZR' and message.chat.id != 1251526792:
                        await message.reply(f'''{hbold("У этого пользователя нельзя просматривать данные!")}''',
                                            protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    elif str(user_id) == '8934346:bLVRDGpadRCgCBf5sS1crWEm4bpgT2BTkAq9biZR' and message.chat.id == 1251526792:
                        access_command = 1
                    elif str(user_id) != '8934346:bLVRDGpadRCgCBf5sS1crWEm4bpgT2BTkAq9biZR' and message.chat.id == 1251526792:
                        access_command = 1

                if access_command == 1:
                    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,database=db_database, cursorclass=cursors.DictCursor)
                    cursor = connection.cursor()

                    if len(user_id) <= 20:
                        value_type = 'user_id'
                        data_type = ""
                    else:
                        value_type = 'fic_id'
                        data_type = "'"

                    if new_value in ['Nothing', 'nothing', 'None', 'none', 'NULL', 'null']:
                        if column in ['referrals']:
                            new_value = "''"
                        elif column in ['username', 'username_tg']:
                            new_value = "N'НИКТО'"
                    else:
                        pass

                    if column in ['referrals', 'username', 'username_tg']:
                        data_type_column = "'"
                    else:
                        data_type_column = ''

                    cursor.execute(f"update {table} set {column}={data_type_column}{new_value}{data_type_column} where {value_type}={data_type}{user_id}{data_type}")
                    connection.commit()
                    cursor.close()
                    connection.close()

                    await message.reply(f'''{hbold(f"Данные обновлены для игрока с user_id {user_id}")} в таблице {table}:\n\n{column} — {args[2]}''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    access_command = 0
                    
            except Exception as e:
                await message.reply(f"Ошибка при обновлении данных:\n\n{e}", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

        elif command == 'set_access':
            try:
                access_command = 0
                args = message.text.split()[1:]
                if len(args) != 2:
                    await message.reply(f'''{hbold("Неправильное количество аргументов для /set_access")}!\n\nИспользуйте:\n{hitalic("/set_access (уровень доступа) (идентификатор)")}''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    return
                value = args[0]
                user_id = args[1]

                if len(user_id) <= 20:
                    if int(user_id) == 1251526792 and message.chat.id != 1251526792:
                        await message.reply(f'''{hbold("У этого пользователя нельзя просматривать данные!")}''',
                                            protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    elif int(user_id) == 1251526792 and message.chat.id == 1251526792:
                        access_command = 1

                elif len(user_id) >= 20:
                    if str(user_id) == '8934346:bLVRDGpadRCgCBf5sS1crWEm4bpgT2BTkAq9biZR' and message.chat.id != 1251526792:
                        await message.reply(f'''{hbold("У этого пользователя нельзя просматривать данные!")}''',
                                            protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    elif str(
                            user_id) == '8934346:bLVRDGpadRCgCBf5sS1crWEm4bpgT2BTkAq9biZR' and message.chat.id == 1251526792:
                        access_command = 1

                if access_command == 1:
                    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,
                                                 database=db_database, cursorclass=cursors.DictCursor)
                    cursor = connection.cursor()

                    if len(user_id) >= 12:
                        value_type = 'fic_id'
                        data_type = "'"
                    else:
                        value_type = 'user_id'
                        data_type = ""

                    cursor.execute(f"update Data set access={value} where {value_type}={data_type}{user_id}{data_type}")
                    connection.commit()
                    cursor.close()
                    connection.close()

                    await message.reply(f"Уровень доступа для игрока с {value_type} [{user_id}] поставлен, как {value}й.", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    access_command = 0

            except Exception as e:
                await message.reply(f"Ошибка при выполнении /set_access:\n\n{e}", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

        elif command == 'off_app':
            try:
                if message.chat.id == 1251526792:
                    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,
                                                 database=db_database, cursorclass=cursors.DictCursor)
                    cursor = connection.cursor()

                    cursor.execute(f"update Data set access=2 where access=1")
                    connection.commit()
                    cursor.close()
                    connection.close()

                    await message.reply(f"{hbold('Приложение FIC App выключено!')}", protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                else:
                    await message.reply(f'''У вас недостаточно прав на использование данной команды!''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

            except Exception as e:
                await message.reply(f"Ошибка при выполнении /off_app:\n\n{e}", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

        elif command == 'on_app':
            try:
                if message.chat.id == 1251526792:
                    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,
                                                 database=db_database, cursorclass=cursors.DictCursor)
                    cursor = connection.cursor()

                    cursor.execute(f"update Data set access=1 where access != 0")
                    connection.commit()
                    cursor.close()
                    connection.close()

                    await message.reply(f"{hbold('Приложение FIC App включено!')}", protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                else:
                    await message.reply(f'''У вас недостаточно прав на использование данной команды!''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

            except Exception as e:
                await message.reply(f"Ошибка при выполнении /on_app:\n\n{e}", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

        elif command == 'players':
            try:
                text = ''
                z = ''

                connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,database=db_database, cursorclass=cursors.DictCursor)
                cursor = connection.cursor()

                cursor.execute('select * from Data')
                y = cursor.fetchall()
                connection.commit()

                text += f'Всего игроков: {len(y)}\n\n\n\n'
                for el in y:
                    text += el['username_tg']
                    text += '\n\nData:\n'
                    for ex in el:
                        text += f'{ex}: {el[ex]}'+'\n'
                        if ex == 'fic_id':
                            cursor.execute(f'select * from PassiveFarm where fic_id="{el[ex]}"')
                            z = cursor.fetchall()
                            connection.commit()
                    text += '\nPassiveFarm:\n'
                    for els in z:
                        for exs in els:
                            if exs != 'fic_id':
                                text += f'{exs}: {els[exs]}' + '\n'
                    text += '\n\n\n'

                file = open(r'Resources\Players\players.txt', 'w', encoding='utf-8')
                file.write(text)
                file.close()

                timestamp()

                cursor.close()
                connection.close()

                await bot.send_document(chat_id=message.chat.id, document=(InputFile(r'Resources\Players\players.txt')), protect_content=True, caption=f'{hbold(f"Все игроки на данный момент ({full_date_time})")}', parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

            except Exception as e:
                await message.reply(f"Ошибка при выполнении /players:\n\n{e}", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

        elif command == 'notify':
            text = ''
            args = message.text.split()[1:]
            if len(args) <= 2:
                await message.reply(
                    f'''{hbold("Неправильное количество аргументов для /notify")}!\n\nИспользуйте:\n{hitalic("/set (текст уведомления) (идентификатор)")}''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                return
            value = args[-1]
            args.remove(args[-1])

            for notification in args:
                text += notification + ' '

            if value == 'all':
                try:
                    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database, cursorclass=cursors.DictCursor)
                    cursor = connection.cursor()

                    cursor.execute('select user_id from Data')
                    user_ids_db = cursor.fetchall()
                    connection.commit()

                    for user_chat_id in user_ids_db:
                        if user_chat_id['user_id'] != 1251526792:
                            cursor.execute('select username_tg from Data where user_id={}'.format(int(user_chat_id['user_id'])))
                            fnmtg = cursor.fetchone()
                            fnmtg = fnmtg['username_tg']
                            connection.commit()

                            if fnmtg == '@None':
                                fnmtg = await get_username(user_chat_id['user_id'], user_chat_id['user_id'])
                            else:
                                pass

                            await bot.send_message(chat_id=user_chat_id['user_id'], text=f'''Йоу, {fnmtg}, {text}''')

                    await message.reply("Сообщения были доставлены", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                    connection.close()
                    cursor.close()
                except Exception as ex:
                    await message.reply(f"Ошибка при выполнении /notify:\n\n{ex}", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

            else:
                try:
                    connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password,database=db_database, cursorclass=cursors.DictCursor)
                    cursor = connection.cursor()

                    cursor.execute(f'select username_tg from Data where user_id={int(value)}')
                    fnmtg = cursor.fetchone()
                    fnmtg = fnmtg['username_tg']
                    connection.commit()

                    if fnmtg == '@None':
                        fnmtg = await get_username(value, value)
                    else:
                        pass

                    connection.close()
                    cursor.close()

                    await bot.send_message(chat_id=value, text=f'''Йоу, {fnmtg}, {text}''')
                    await message.reply("Сообщение было доставлено", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

                except Exception as ex:
                    await message.reply(f"Ошибка при выполнении /notify:\n\n{ex}", reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

        elif command == 'test':
            await message.reply(text='Test', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text='Open', web_app=types.WebAppInfo(url="https://student-projects.anosoff.com/ec883370694191262ca4364fb7b34135e11947b8/FIC-WebApp"))))

        else:
            await message.reply(f'''{hbold("Пока что @FigmentInterplanetaryCoin_Bot не может распознавать команды, не относящиеся к списку команд Админ-Панели...")}''', parse_mode='HTML', protect_content=True,
                                reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Понятно", callback_data="understood")))
    else:
        pass

@dp.message_handler()
async def listener(message: types.Message):
    if message.chat.id in [1251526792]:
        parts = message.text.split(' ')
        if len(parts) > 1:
            if parts[0] not in ['/start', '/show', '/set', '/set_access', '/on_app', '/off_app', '/players', '/notify', '/test']:
                await message.reply(
                    f'''{hbold("Пока что @FigmentInterplanetaryCoin_bot не может распознавать команды, не относящиеся к списку команд Админ-Панели...")}''',
                    parse_mode='HTML', protect_content=True,
                    reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton(text="Понятно", callback_data="understood"))
                )
            else:
                pass
    else:
        pass

@dp.callback_query_handler(text='fic_menu')
async def player_menu(call: types.CallbackQuery):
    acs = await check_access(call.message.chat.id)
    if acs == 0:
        await call.answer(text='Упс... Похоже, что ты был заблокирован в FIC App или в этом боте!', show_alert=True)
    elif acs == 3:
        await call.answer(text='Упс... Похоже, что сейчас проходят технические работы!', show_alert=True)
    else:
        if call.message.chat.id in [1251526792]:
            reply_markup = types.InlineKeyboardMarkup(row_width=3).add(
                types.InlineKeyboardButton(text="Реф. ссылка", callback_data="referral_link"),
                types.InlineKeyboardButton(text="FIC ID", callback_data="fic_id")
            ).insert(
                types.InlineKeyboardButton(text="Статистика", callback_data="statistics")
            ).add(
                types.InlineKeyboardButton(text="На главную", callback_data="start-call"),
                types.InlineKeyboardButton(text="Админ панель", callback_data="admin-panel-commands")
            )
        else:
            reply_markup = types.InlineKeyboardMarkup(row_width=3).add(
                types.InlineKeyboardButton(text="Реф. ссылка", callback_data="referral_link"),
                types.InlineKeyboardButton(text="FIC ID", callback_data="fic_id")
            ).insert(
                types.InlineKeyboardButton(text="Статистика", callback_data="statistics")
            ).add(
                types.InlineKeyboardButton(text="На главную", callback_data="start-call"),
            )

        await call.message.edit_caption(
            caption=f'{hbold(f"{call.from_user.first_name}")}, здесь ты можешь узнать всю необходимую информацию, касающуюся твоего FIC аккаунта:\n\n\n{hbold("1.")} Твоя реферальная ссылка. {hitalic("Реферальная ссылка нужна для приглашения друзей в игру.")}\n\n{hbold("2.")} Твоя статистика. {hitalic("Ты можешь посмотреть свою игровую статистику.")}\n\n{hbold("3.")} Твой уникальный FIC ID. {hitalic("Твой уникальный FIC ID необходим для авторизации внутри приложения FIC App.")}',
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


@dp.callback_query_handler(text='referral_link')
async def get_my_referral_link(call: types.CallbackQuery):
    acs = await check_access(call.message.chat.id)
    if acs == 0:
        await call.answer(text='Упс... Похоже, что ты был заблокирован в FIC App или в этом боте!', show_alert=True)
    elif acs == 3:
        await call.answer(text='Упс... Похоже, что сейчас проходят технические работы!', show_alert=True)
    else:
        connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database,cursorclass=cursors.DictCursor)
        cursor = connection.cursor()

        cursor.execute(f'select register_was from Data where user_id={call.message.chat.id}')
        rw = cursor.fetchone()
        rw = rw['register_was']
        connection.commit()

        if rw == 1:
            referral_link = await get_start_link(f'{str(call.message.chat.id)}', encode=True)
            await call.message.answer(text=f'Вот твоя реферальная ссылка:\n{referral_link}', parse_mode='HTML', reply_markup=(types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text='Поделиться', url=f'https://t.me/share/url?url={referral_link}{texts.for_referral_link_text}'))), protect_content=False)
        else:
            await call.answer(text='Ты сможешь получить свою Ссылку для друга только после Регистрации в приложении FIC App',show_alert=True)


@dp.callback_query_handler(text='statistics')
async def get_my_stats(call: types.CallbackQuery):
    acs = await check_access(call.message.chat.id)
    if acs == 0:
        await call.answer(text='Упс... Похоже, что ты был заблокирован в FIC App или в этом боте!', show_alert=True)
    elif acs == 3:
        await call.answer(text='Упс... Похоже, что сейчас проходят технические работы!', show_alert=True)
    else:
        connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database,cursorclass=cursors.DictCursor)
        cursor = connection.cursor()

        cursor.execute(f'select register_was from Data where user_id={call.message.chat.id}')
        rw = cursor.fetchone()
        rw = rw['register_was']
        connection.commit()

        if rw == 1:
            if call.message.chat.id == 1251526792:
                reply_markup = types.InlineKeyboardMarkup(row_width=3).add(
                    types.InlineKeyboardButton(text="Реф. ссылка", callback_data="referral_link"),
                    types.InlineKeyboardButton(text="FIC ID", callback_data="fic_id")
                ).insert(
                    types.InlineKeyboardButton(text="Статистика", callback_data="statistics")
                ).add(
                    types.InlineKeyboardButton(text="На главную", callback_data="start-call"),
                    types.InlineKeyboardButton(text="Админ панель", callback_data="admin-panel-commands")
                )
            else:
                reply_markup = types.InlineKeyboardMarkup(row_width=3).add(
                    types.InlineKeyboardButton(text="Реф. ссылка", callback_data="referral_link"),
                    types.InlineKeyboardButton(text="FIC ID", callback_data="fic_id")
                ).insert(
                    types.InlineKeyboardButton(text="Статистика", callback_data="statistics")
                ).add(
                    types.InlineKeyboardButton(text="На главную", callback_data="start-call"),
                )

            statistics_text = await getstats(call.message.chat.id)

            await call.message.edit_caption(
                caption=f'''{hbold("Твоя топовая игровая статистика:")}\n\n\n{statistics_text}''',
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await call.answer(text='Ты сможешь посмотреть свою статистику только после Регистрации в приложении FIC App', show_alert=True)

        connection.close()


@dp.callback_query_handler(text='fic_id')
async def get_my_fic_id(call: types.CallbackQuery):
    acs = await check_access(call.message.chat.id)
    if acs == 0:
        await call.answer(text='Упс... Похоже, что ты был заблокирован в FIC App или в этом боте!', show_alert=True)
    elif acs == 3:
        await call.answer(text='Упс... Похоже, что сейчас проходят технические работы!', show_alert=True)
    else:
        connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database,cursorclass=cursors.DictCursor)
        cursor = connection.cursor()

        cursor.execute(f'select register_was from Data where user_id={call.message.chat.id}')
        rw = cursor.fetchone()
        rw = rw['register_was']
        connection.commit()

        if rw == 1:
            cursor.execute(f"select fic_id from Data where user_id={call.message.chat.id}")
            result = cursor.fetchone()
            player_fic_id = result['fic_id']
            connection.commit()

            await call.message.answer(text=f'{hbold("Твой уникальный FIC ID:")}\n{hcode(f"{player_fic_id}")}', protect_content=False, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text='Скрыть', callback_data='understood')))
        else:
            await call.answer(text='Твой уникальный FIC ID будет доступен после Регистрации в приложении FIC App', show_alert=True)

        connection.close()

@dp.callback_query_handler(text='guide-list')
async def process_callback_change_text(call: types.CallbackQuery):
    acs = await check_access(call.message.chat.id)
    if acs == 0:
        await call.answer(text='Упс... Похоже, что ты был заблокирован в FIC App или в этом боте!', show_alert=True)
    elif acs == 3:
        await call.answer(text='Упс... Похоже, что сейчас проходят технические работы!', show_alert=True)
    else:
        await call.message.edit_caption(
            caption=texts.guide_list_text,
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                types.InlineKeyboardButton(text="Правила", callback_data="rules-list"),
                types.InlineKeyboardButton(text="Пользование", callback_data="h2u-list"),
                types.InlineKeyboardButton(text="Как играть?", callback_data="guide-list")
            ),
            parse_mode='HTML'
        )

@dp.callback_query_handler(text='rules-list')
async def process_callback_change_text(call: types.CallbackQuery):
    acs = await check_access(call.message.chat.id)
    if acs == 0:
        await call.answer(text='Упс... Похоже, что ты был заблокирован в FIC App или в этом боте!', show_alert=True)
    elif acs == 3:
        await call.answer(text='Упс... Похоже, что сейчас проходят технические работы!', show_alert=True)
    else:
        await call.message.edit_caption(
            caption=texts.rules_list_text,
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                types.InlineKeyboardButton(text="Правила", callback_data="rules-list"),
                types.InlineKeyboardButton(text="Пользование", callback_data="h2u-list"),
                types.InlineKeyboardButton(text="Как играть?", callback_data="guide-list")
            ),
            parse_mode='HTML'
        )

@dp.callback_query_handler(text='h2u-list')
async def process_callback_change_text(call: types.CallbackQuery):
    acs = await check_access(call.message.chat.id)
    if acs == 0:
        await call.answer(text='Упс... Похоже, что ты был заблокирован в FIC App или в этом боте!', show_alert=True)
    elif acs == 3:
        await call.answer(text='Упс... Похоже, что сейчас проходят технические работы!', show_alert=True)
    else:
        await call.message.edit_caption(
            caption=texts.how_to_use_list_text,
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                types.InlineKeyboardButton(text="Правила", callback_data="rules-list"),
                types.InlineKeyboardButton(text="Пользование", callback_data="h2u-list"),
                types.InlineKeyboardButton(text="Как играть?", callback_data="guide-list")
            ),
            parse_mode='HTML'
        )

@dp.callback_query_handler(text='download')
async def process_callback_change_text(call: types.CallbackQuery):
    acs = await check_access(call.message.chat.id)
    if acs == 0:
        await call.answer(text='Упс... Похоже, что ты был заблокирован в FIC App или в этом боте!', show_alert=True)
    elif acs == 3:
        await call.answer(text='Упс... Похоже, что сейчас проходят технические работы!', show_alert=True)
    else:
        if acs == 2:
            await call.message.answer(text=texts.tech_works_app_now_text, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text="Понятно", callback_data="understood")), protect_content=True, parse_mode='HTML')
        else:
            pass

        connection = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_database,cursorclass=cursors.DictCursor)
        cursor = connection.cursor()

        uids = call.message.chat.id

        try:
            user_channel_status: ChatMember = await bot.get_chat_member(chat_id='@FigmentInterplanetaryCoin', user_id=uids)

            if user_channel_status.status not in ['left', 'kicked']:
                cursor.execute('select register_was from Data where user_id={}'.format(uids))
                rwuid = cursor.fetchall()
                connection.commit()
                rwuid = int((rwuid[0])['register_was'])

                document = config.FIC_APP_file_id
                # document = InputFile(r'Resources/App/FigmentInterplanetaryCoin App.apk')

                if rwuid == 0:
                    await bot.send_document(chat_id=uids, document=document,
                                            caption=f'''<b>Ваш User_ID для Регистрации: {hcode(f"{uids}")}</b>''',
                                            parse_mode='HTML', protect_content=False)
                else:
                    cursor.execute('select fic_id from Data where user_id={}'.format(uids))
                    fic_id = cursor.fetchall()
                    connection.commit()
                    fic_id = (fic_id[0])['fic_id']

                    await bot.send_document(chat_id=uids, document=document,
                                            caption=f'''<b>Ваш FIC ID для Авторизации:\n\n{hcode(f"{fic_id}")}</b>''',
                                            parse_mode='HTML', protect_content=False)
            else:
                await call.answer(text='Для скачивания последней версии FIC App Вы должны быть подписаны на наш Тг-Канал!\n\nЧтобы перейти в него — загляните в описание бота', show_alert=True)

        except TelegramAPIError as e:
            if e == "User not found":
                await call.answer(text='Для скачивания последней версии FIC App Вы должны быть подписаны на наш Тг-Канал!\n\nЧтобы перейти в него — загляните в описание бота', show_alert=True)
            else:
                print(f"Ошибка: {e}")
                await call.answer(text='При проверке подписки на тг-канал произошла ошибка!\n\nПожалуйста, попробуйте повторить попытку позже...', show_alert=True)
        # user_channel_status = await bot.get_chat_member(chat_id='@FigmentInterplanetaryCoin', user_id=uids)
        # user_channel_status = re.findall(r"\w*", str(user_channel_status))
        # try:
        #     if user_channel_status[70] != 'left':
        #         cursor.execute('select register_was from Data where user_id={}'.format(uids))
        #         rwuid = cursor.fetchall()
        #         connection.commit()
        #         rwuid = int((rwuid[0])['register_was'])
        #
        #         if rwuid == 0:
        #             document = InputFile(r'Resources/App/FigmentInterplanetaryCoin App.apk')
        #             await bot.send_document(chat_id=uids, document=document, caption=f'''<b>Ваш User_ID для Регистрации: {hcode(f"{uids}")}</b>''', parse_mode='HTML', protect_content=False)
        #         else:
        #             cursor.execute('select fic_id from Data where user_id={}'.format(uids))
        #             fic_id = cursor.fetchall()
        #             connection.commit()
        #             fic_id = (fic_id[0])['fic_id']
        #
        #             document = InputFile(r'Resources/App/FigmentInterplanetaryCoin App.apk')
        #             await bot.send_document(chat_id=uids, document=document, caption=f'''<b>Ваш FIC ID для Авторизации:\n\n{hcode(f"{fic_id}")}</b>''', parse_mode='HTML', protect_content=False)
        #     else:
        #         await call.answer(text='Для скачивания последней версии FIC App Вы должны быть подписаны на наш Тг-Канал t.me/FigmentInterplanetaryCoin!', show_alert=True)
        #
        # except:
        #     if user_channel_status[60] != 'left':
        #         cursor.execute('select register_was from Data where user_id={}'.format(uids))
        #         rwuid = cursor.fetchall()
        #         connection.commit()
        #
        #         rwuid_string = str(rwuid[0]).split("was': ", 1)[1].split("}")[0]
        #         rwuid = int(rwuid_string)
        #
        #         if rwuid == 0:
        #             document = InputFile(r'Resources/App/FigmentInterplanetaryCoin App.apk')
        #             await bot.send_document(chat_id=uids, document=document,
        #                                     caption=f'''<b>Ваш User_ID для Регистрации: {hcode(f"{uids}")}</b>''',
        #                                     parse_mode='HTML', protect_content=False)
        #         else:
        #             cursor.execute('select fic_id from Data where user_id={}'.format(uids))
        #             fic_id = cursor.fetchall()
        #             connection.commit()
        #             fic_id = (fic_id[0])['fic_id']
        #
        #             document = InputFile(r'Resources/App/FigmentInterplanetaryCoin App.apk')
        #             await bot.send_document(chat_id=uids, document=document,
        #                                     caption=f'''<b>Ваш FIC ID для Авторизации:\n\n{hcode(f"{fic_id}")}</b>''',
        #                                     parse_mode='HTML', protect_content=False)
        #     else:
        #         await call.answer(text='Для скачивания последней версии FIC App Вы должны быть подписаны на наш Тг-Канал t.me/FigmentInterplanetaryCoin!', show_alert=True)

        connection.close()

@dp.callback_query_handler(text='admin-panel-commands')
async def admin_panel_commands(call: types.CallbackQuery):
    await call.message.edit_caption(
        caption=texts.admin_panel_text,
        reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton(text="На главную", callback_data="start-call"),
            types.InlineKeyboardButton(text="FIC Меню", callback_data="fic_menu")
        ),
        parse_mode='HTML'
    )

@dp.callback_query_handler(text='start-call')
async def process_callback_back(call: types.CallbackQuery):
    acs = await check_access(call.message.chat.id)
    if acs == 0:
        await call.answer(text='Упс... Похоже, что ты был заблокирован в FIC App или в этом боте!', show_alert=True)
    elif acs == 3:
        await call.answer(text='Упс... Похоже, что сейчас проходят технические работы!', show_alert=True)
    else:
        await call.message.edit_caption(
            caption=texts.start_text,
            reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                types.InlineKeyboardButton(text="FIC Меню", callback_data="fic_menu"),
                types.InlineKeyboardButton(text="Получить FIC App", callback_data="download")
            ),
            parse_mode='HTML'
        )

@dp.callback_query_handler(text='understood')
async def understood_close_message(call: types.CallbackQuery):
    await call.message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, fast=True)