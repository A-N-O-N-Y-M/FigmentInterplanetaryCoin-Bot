from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from aiogram.utils.markdown import hbold, hitalic

import sqlite3
from datetime import datetime

import texts
import config


API_TOKEN = config.API_TOKEN_SUPPORT

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['question', 'my_questions', 'questions', 'close_question', 'answer', 'start', 'idea', 'my_ideas', 'ideas', 'accept'])
async def questions_handler(message: types.Message):
    command = message.text.split()[0][1:]

    if command == 'start':
        reply_markup = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton(text='Как работает бот', callback_data='how_this_bot_works'),
            types.InlineKeyboardButton(text='Как поинтересоваться', callback_data='how_do_question')
        )
        if message.chat.id in ["Admins UID"]:
            reply_markup.add(types.InlineKeyboardButton(text='Админ панель', callback_data='admin_panel'))

        await bot.send_photo(
            photo=InputFile(r'Resources/Images/FIC Logo Strong.png'),
            chat_id=message.chat.id,
            caption=texts.start_support_text,
            reply_markup=reply_markup,
            protect_content=True,
            parse_mode='HTML'
        )

    elif command == 'question':
        try:
            connection = sqlite3.connect('Resources/Data/DataBase.db')
            cursor = connection.cursor()

            question_text = message.text.split('/question ')[1]
            question_heading = question_text.split('?')[0]
            question_heading += '?'

            question_text = question_text.split('?')[1]
            question_text = question_text.lstrip()
            question_text = question_text.replace('\n', ' ')

            now = datetime.now()
            date = now.strftime('%d.%m.%Y')
            time = now.strftime('%H:%M:%S')

            cursor.execute(f'insert into Data(user_id, username, first_name, question_date, question_time, question_heading, question_text, question_answer, question_opening) values({message.chat.id}, "{message.from_user.username}", "{message.from_user.first_name}", "{date}", "{time}", "{question_heading}", "{question_text}", "", 0)')
            connection.commit()
            connection.close()

            await message.answer(text='Вопрос был задан Разработчику!\n\nОжидайте ответа в этом боте', protect_content=True)
            connection = sqlite3.connect('Resources/Data/DataBase.db')
            cursor = connection.cursor()
            cursor.execute('select * from Data')
            fetch = cursor.fetchall()
            connection.commit()
            connection.close()

            await bot.send_message(chat_id="Owner UID", text=f'Только что был задан новый вопрос от @{message.from_user.username}!\n\nВопрос был записан под номером {hbold(f"#{len(fetch)}")}', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton(text="Удалить", callback_data="understood")
            ), parse_mode='HTML')

        except Exception as ex:
            await message.reply(
                f'''Эта команда нужна для того, чтобы интересоваться у Разработчика, нужно задавать вопрос так:\n\n/question <Сам вопрос?> <Полное описание вопроса>''',
                reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                    types.InlineKeyboardButton(text="Понятно", callback_data="understood")))

    elif command == 'my_questions':
        connection = sqlite3.connect('Resources/Data/DataBase.db')
        cursor = connection.cursor()
        cursor.execute(f'select * from Data where user_id="{message.chat.id}"')
        fetch = cursor.fetchall()
        connection.commit()
        connection.close()

        result = ''
        counter = 0
        for el in fetch:
            result += f'''{counter+1}. <b>"{el[6]}"</b>\nНомер в списке вопросов: #{el[0]}\nТекст вопроса: {hitalic(f'"{el[7]}"')}\nДата и время: {el[4]} {el[5]}\nОтвет Разработчика: '''
            if (el[8] != '') or (el[8] is not None) or (el[8] != ' '):
                result += f'''{hitalic(f'"{el[8]}"')}'''
            elif (el[8] == '') or (el[8] is None) or (el[8] == ' '):
                result += f'{hitalic("Без ответа")}'

            if el[9] == 0:
                result += f'\n{hbold("Вопрос открыт")}'
            elif el[9] == 1:
                result += f'\n{hbold("Вопрос закрыт")}'

            if counter < (len(fetch) - 1):
                result += '\n\n'
                counter += 1
            elif counter == len(fetch) or len(fetch) == 1:
                pass

        if len(fetch) != 0:
            await message.answer(text=f'''{hbold(f"Всего заданных вами вопросов — {len(fetch)}:")}\n\n{result}''',protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=2).add(types.InlineKeyboardButton(text='Открытые', callback_data='opened_questions_show'), types.InlineKeyboardButton(text='Закрытые', callback_data='closed_questions_show')))
        else:
            await message.answer(text=f'''Пока что вы не задали ни одного вопроса Разработчику!''')

    elif command == 'close_question':
        args = message.text.split()[1:]

        if len(args) >= 2:
            await message.reply(
                f'''{hbold("Неправильное количество аргументов для /close_question")}!\n\nИспользуйте:\n{hitalic("/close_question (Номер вашего вопроса)")}''',
                protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                    types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
            return

        elif len(args) == 0:
            await message.reply(
                f'''Эта команда нужна для того, чтобы закрыть свой определенный вопрос, нужно использовать команду так:\n\n/close_question <Номер вашего вопроса>''',
                protect_content=True, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                    types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
            return

        question_number = args[0]

        try:
            connection = sqlite3.connect('Resources/Data/DataBase.db')
            cursor = connection.cursor()
            cursor.execute(f'select question_heading, user_id from Data where id={question_number}')
            fetch = cursor.fetchone()
            connection.commit()

            question_heading = fetch[0]
            question_heading = str(question_heading)
            user_id = fetch[1]
            user_id = int(user_id)

            if message.chat.id == user_id:
                cursor.execute(f'update Data set question_opening=1 where id={question_number}')
                connection.commit()

                await message.reply(text=f'''Ваш вопрос "{question_heading}" был успешно закрыт!''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
                await bot.send_message(chat_id=1251526792, text=f'''Вопрос {hbold(f'"{question_heading}"')} был закрыт автором!''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
            else:
                await message.reply(
                    text=f'''{hbold("При попытке закрыть вопрос произошла ошибка!")}\n\nПожалуйста, повторите попытку позже.''',
                    protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

            connection.close()

        except Exception as ex:
            await message.reply(text=f'''{hbold("При попытке закрыть вопрос произошла ошибка!")}\n\nПожалуйста, повторите попытку позже.''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                    types.InlineKeyboardButton(text="Удалить", callback_data="understood")))

    elif command == 'questions':
        if message.chat.id == "Owner UID":
            connection = sqlite3.connect('Resources/Data/DataBase.db')
            cursor = connection.cursor()
            cursor.execute('select * from Data where question_opening=0')
            x = cursor.fetchall()
            connection.commit()

            cursor.execute('select * from Data where question_opening=1')
            y = cursor.fetchall()
            connection.commit()

            connection.close()

            result_opened = ''
            counter_opened = 0
            result_closed = ''
            counter_closed = 0

            if len(x) != 0:
                for el1 in x:
                    result_opened += f'#{el1[0]}: <b>"{el1[6]}"</b>\nДата и время: {el1[4]} {el1[5]}\nАвтор: {el1[3]}/@{el1[2]}/<code>{el1[1]}</code>'
                    if counter_opened < len(x):
                        result_opened += '\n\n'
                        counter_opened += 1
                    elif counter_opened == len(x) or len(x) == 1:
                        pass
            else:
                result_opened = f'<i>Сейчас нет вопросов, на которые следует ответить.\nОтличная работа!</i>'

            if len(y) != 0:
                for el2 in y:
                    result_closed += f'#{el2[0]}: <b>"{el2[6]}"</b>\nДата и время: {el2[4]} {el2[5]}\nАвтор: {el2[3]}/@{el2[2]}/<code>{el2[1]}</code>'
                    if counter_closed < len(y):
                        result_closed += '\n\n'
                        counter_closed += 1
                    elif counter_closed == len(y) or len(y) == 1:
                        pass
            else:
                result_closed = f'<i>Сейчас нет закрытых вопросов.</i>'

            if len(y) == len(x) == 0:
                await message.answer(text=f'''{hbold("На данный момент никто не задал вопрос!")}\n\nОстается только ждать.''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
            else:
                await message.answer(text=f'''{hbold(f"Всего вопросов, ожидающих ответа — {len(x)}:")}\n\n{result_opened}\n\n\n{hbold(f"Всего закрытых вопросов — {len(y)}:")}\n\n{result_closed}''', protect_content=True, parse_mode='HTML')

        else:
            pass

    elif command == 'answer':
        args = message.text.split()[1:]
        answer_text_text = ''

        if len(args) < 2:
            await message.reply(
                f'''{hbold("Неправильное количество аргументов для /answer")}!\n\nИспользуйте:\n{hitalic("/answer (номер вопроса) (ответ на вопрос)")}''',
                protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                    types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
            return

        question_num = args[0]
        question_num = question_num.lstrip()
        args.remove(args[0])

        connection = sqlite3.connect('Resources/Data/DataBase.db')
        cursor = connection.cursor()
        cursor.execute(f'select question_answer, question_opening from Data where id={question_num}')
        fetch = cursor.fetchone()
        connection.commit()
        connection.close()

        if fetch[1] == 0:
            if fetch[0] == '' or fetch[0] is None:
                counter = 0
                for answer_result_text in args:
                    answer_text_text += answer_result_text

                    if counter < (len(args) - 1):
                        counter += 1
                        answer_text_text += ' '

                    elif counter == len(args):
                        counter += 1

                connection = sqlite3.connect('Resources/Data/DataBase.db')
                cursor = connection.cursor()
                cursor.execute(f'update Data set question_answer="{answer_text_text}" where id={question_num}')
                connection.commit()
                cursor.execute(f'select user_id, question_heading from Data where id={question_num}')
                fetch = cursor.fetchone()
                connection.commit()
                connection.close()

                await bot.send_message(chat_id=fetch[0], text=f'''<b>На ваш вопрос "{hitalic(f"{fetch[1]}")}" поступил ответ:</b>\n\n{answer_text_text.replace('n', 'n')}''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                         types.InlineKeyboardButton(text="Закрыть вопрос", callback_data="close_question")))
            else:
                await message.reply(text='Вы не можете ответить на данный вопрос второй раз!', protect_content=True)
        else:
            await message.reply(text='Вы не можете ответить на данный вопрос, так как он был закрыт!', protect_content=True)

    elif command == 'idea':
        try:
            connection = sqlite3.connect('Resources/Data/DataBase.db')
            cursor = connection.cursor()

            idea_text = message.text.split('/idea ')[1]

            idea_text = idea_text.lstrip()
            idea_text = idea_text.replace('\n', ' ')

            now = datetime.now()
            date = now.strftime('%d.%m.%Y')
            time = now.strftime('%H:%M:%S')

            cursor.execute(
                f'insert into Ideas(user_id, username, first_name, idea_date, idea_time, idea_text, idea_accepted) values({message.chat.id}, "{message.from_user.username}", "{message.from_user.first_name}", "{date}", "{time}", "{idea_text}", 0)')
            connection.commit()
            connection.close()

            await message.answer(text='Ваша идея была предложена Разработчику!\n\nОжидайте уведомления одобрения/отклонения в этом боте',
                                 protect_content=True)
            connection = sqlite3.connect('Resources/Data/DataBase.db')
            cursor = connection.cursor()
            cursor.execute('select * from Ideas')
            fetch = cursor.fetchall()
            connection.commit()
            connection.close()

            await bot.send_message(chat_id=1251526792,
                                   text=f'Только что была предложения идея от @{message.from_user.username}!\n\nИдея была записана под номером {hbold(f"#{len(fetch)}")}',
                                   reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                       types.InlineKeyboardButton(text="Удалить", callback_data="understood")
                                   ), parse_mode='HTML')

        except Exception as ex:
            await message.reply(
                f'''Эта команда нужна для того, чтобы предлагать свои идеи для проекта Разработчику, пользоваться ей нужно так:\n\n/idea <Ваше предложение>''',
                reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                    types.InlineKeyboardButton(text="Понятно", callback_data="understood")))

    elif command == 'ideas':
        if message.chat.id == "Owner UID":
            connection = sqlite3.connect('Resources/Data/DataBase.db')
            cursor = connection.cursor()
            cursor.execute('select * from Ideas where idea_accepted=0')
            x = cursor.fetchall()
            connection.commit()

            cursor.execute('select * from Ideas where idea_accepted=1')
            y = cursor.fetchall()
            connection.commit()

            cursor.execute('select * from Ideas where idea_accepted=2')
            z = cursor.fetchall()
            connection.commit()
            connection.close()

            result_under_consideration = ''
            counter_under_consideration = 0
            result_accepted = ''
            counter_accepted = 0
            result_rejected = ''
            counter_rejected = 0

            if len(x) != 0:
                for el1 in x:
                    result_under_consideration += f'#{el1[0]}: <b>"{el1[6]}"</b>\nДата и время: {el1[4]} {el1[5]}\nАвтор: {el1[3]}/@{el1[2]}/<code>{el1[1]}</code>'
                    if counter_under_consideration < len(x):
                        result_under_consideration += '\n\n'
                        counter_under_consideration += 1
                    elif counter_under_consideration == len(x) or len(x) == 1:
                        pass
            else:
                result_under_consideration = '<i>Сейчас нет идей, которые находятся на этапе рассмотрения.</i>'

            if len(y) != 0:
                for el2 in y:
                    result_accepted += f'#{el2[0]}: <b>"{el2[6]}"</b>\nДата и время: {el2[4]} {el2[5]}\nАвтор: {el2[3]}/@{el2[2]}/<code>{el2[1]}</code>'
                    if counter_accepted < len(y):
                        result_accepted += '\n\n'
                        counter_accepted += 1
                    elif counter_accepted == len(y) or len(y) == 1:
                        pass
            else:
                result_accepted = '<i>Сейчас нет принятых к сведению идей</i>'

            if len(z) != 0:
                for el3 in z:
                    result_rejected += f'#{el3[0]}: <b>"{el3[6]}"</b>\nДата и время: {el3[4]} {el3[5]}\nАвтор: {el3[3]}/@{el3[2]}/<code>{el3[1]}</code>'
                    if counter_rejected < len(z):
                        result_rejected += '\n\n'
                        counter_rejected += 1
                    elif counter_rejected == len(z) or len(z) == 1:
                        pass
            else:
                result_rejected = '<i>Сейчас нет отклоненных идей.</i>'

            if len(z) == len(y) == len(x) == 0:
                await message.answer(text=f'''{hbold("На данный момент никто не предложил никаких идей!")}\n\nОстается только ждать желающих.''', protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
            else:
                await message.answer(text=f'''{hbold(f"Всего идей, ожидающих рассмотрения — {len(x)}:")}\n\n{result_under_consideration}\n\n\n{hbold(f"Всего принятых идей — {len(y)}:")}\n\n{result_accepted}\n\n\n{hbold(f"Всего отклоненных идей — {len(z)}:")}\n\n{result_rejected}''', protect_content=True, parse_mode='HTML')

        else:
            pass

    elif command == 'my_ideas':
        connection = sqlite3.connect('Resources/Data/DataBase.db')
        cursor = connection.cursor()
        cursor.execute(f'select * from Ideas where user_id="{message.chat.id}"')
        fetch = cursor.fetchall()
        connection.commit()
        connection.close()

        result = ''
        counter = 0
        for el in fetch:
            result += f'''{counter+1}. Идея: <b>"{el[6]}"</b>\nДата и время: {el[4]} {el[5]}\nСтатус рассмотрения: '''

            if el[7] == 0:
                result += f'{hbold("Не рассмотрена")}'
            elif el[7] == 1:
                result += f'{hbold("Принята к сведению")}'
            elif el[7] == 2:
                result += f'{hbold("Отклонена")}'

            if counter < (len(fetch) - 1):
                result += '\n\n'
                counter += 1
            elif counter == len(fetch) or len(fetch) == 1:
                pass

        if len(fetch) != 0:
            await message.answer(text=f'''{hbold(f"Всего предложенных вами идей — {len(fetch)}:")}\n\n{result}''',protect_content=True, parse_mode='HTML',reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                         types.InlineKeyboardButton(text='Не рассмотренные',
                                                                    callback_data='not_checked_ideas_show')).insert(
                                         types.InlineKeyboardButton(text='Принятые',
                                                                    callback_data='accepted_ideas_show')).add(
                                         types.InlineKeyboardButton(text='Отклоненные',
                                                                    callback_data='rejected_ideas_show')))
        else:
            await message.answer(text=f'''Пока что вы не предложили ни одной идеи Разработчику!''')

    elif command == 'accept':
        args = message.text.split()[1:]

        if len(args) != 2:
            await message.reply(
                f'''{hbold("Неправильное количество аргументов для /accept")}!\n\nИспользуйте:\n{hitalic("/accept (номер идеи) (результат рассмотрения)")}''',
                protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                    types.InlineKeyboardButton(text="Удалить", callback_data="understood")))
            return

        idea_num = args[0]
        accept_value = args[1]

        connection = sqlite3.connect('Resources/Data/DataBase.db')
        cursor = connection.cursor()
        cursor.execute(f'select idea_accepted from Ideas where id={idea_num}')
        fetch = cursor.fetchone()
        connection.commit()
        connection.close()

        if fetch[1] == 0:
            if accept_value == 0:
                dict = {
                    1: 'Принята к сведению',
                    2: 'Отклонена'
                }

                if accept_value == 1:
                    reply_markup = types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton(text="Супер", callback_data="close_question"))

                else:
                    reply_markup = types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton(text="Жаль", callback_data="close_question"))

                connection = sqlite3.connect('Resources/Data/DataBase.db')
                cursor = connection.cursor()
                cursor.execute(f'update Data set idea_accepted={accept_value} where id={idea_num}')
                connection.commit()
                cursor.execute(f'select user_id, idea_text from Data where id={idea_num}')
                fetch = cursor.fetchone()
                connection.commit()
                connection.close()

                await bot.send_message(chat_id=fetch[0], text=f'''<b>Ваша идея "{hitalic(f"{fetch[1]}")}" получила статус рассмотрения:</b>\n\n{hitalic(f"{dict[accept_value]}")}''', protect_content=True, parse_mode='HTML', reply_markup=reply_markup)
            else:
                await message.reply(
                    text='Вы не можете изменить результат рассмотрения на данную идею как "На рассмотрении", так как она уже имеет этот статус!',protect_content=True)
        else:
            await message.reply(text='Вы не можете изменить результат рассмотрения на данную идею, так как он уже был дан ранее!', protect_content=True)


@dp.callback_query_handler(text='start_call')
async def how_bot_works(call: types.CallbackQuery):
    if call.message.chat.id in ["Owner UID"]:
        reply_markup = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton(text="Как работает бот", callback_data="how_this_bot_works"),
            types.InlineKeyboardButton(text="Как поинтересоваться", callback_data="how_do_question"),
            types.InlineKeyboardButton(text="Админ панель", callback_data="admin_panel")
        )
    else:
        reply_markup = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton(text="Как работает бот", callback_data="how_this_bot_works"),
            types.InlineKeyboardButton(text="Как поинтересоваться", callback_data="how_do_question")
        )

    reply_markup = types.InlineKeyboardMarkup(row_width=2).add(
        types.InlineKeyboardButton(text='Как работает бот', callback_data='how_this_bot_works'),
        types.InlineKeyboardButton(text='Как поинтересоваться', callback_data='how_do_question')
    )
    if call.message.chat.id in ["Owner UID"]:
        reply_markup.add(types.InlineKeyboardButton(text='Админ панель', callback_data='admin_panel'))

    await call.message.edit_caption(
        caption=texts.start_support_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

@dp.callback_query_handler(text='admin_panel')
async def admin_panel(call: types.CallbackQuery):
    await call.message.edit_caption(
        caption=texts.admin_panel_support_text,
        reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton(text="Назад", callback_data="start_call")
        ),
        parse_mode='HTML'
    )


@dp.callback_query_handler(text='all_my_questions')
async def all_my_questions_func(call: types.CallbackQuery):
    connection = sqlite3.connect('Resources/Data/DataBase.db')
    cursor = connection.cursor()
    cursor.execute(f'select * from Data where user_id="{call.message.chat.id}"')
    fetch = cursor.fetchall()
    connection.commit()
    connection.close()

    result = ''
    counter = 0
    for el in fetch:
        result += f'''{counter + 1}. <b>"{el[6]}"</b>\nНомер в списке вопросов: #{el[0]}\nТекст вопроса: {hitalic(f'"{el[7]}"')}\nДата и время: {el[4]} {el[5]}\nОтвет Разработчика: '''
        if (el[8] != '') or (el[8] is not None) or (el[8] != ' '):
            result += f'''{hitalic(f'"{el[8]}"')}'''
        elif (el[8] == '') or (el[8] is None) or (el[8] == ' '):
            result += f'{hitalic("Без ответа")}'

        if el[9] == 0:
            result += f'\n{hbold("Вопрос открыт")}'
        elif el[9] == 1:
            result += f'\n{hbold("Вопрос закрыт")}'

        if counter < (len(fetch) - 1):
            result += '\n\n'
            counter += 1
        elif counter == len(fetch) or len(fetch) == 1:
            pass

    await call.message.edit_text(text=f'''{hbold(f"Всего заданных вами вопросов — {len(fetch)}:")}\n\n{result}''', parse_mode='HTML',
                         reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                             types.InlineKeyboardButton(text='Открытые', callback_data='opened_questions_show'),
                             types.InlineKeyboardButton(text='Закрытые', callback_data='closed_questions_show')))

@dp.callback_query_handler(text='opened_questions_show')
async def show_opened_questions(call: types.CallbackQuery):
    connection = sqlite3.connect('Resources/Data/DataBase.db')
    cursor = connection.cursor()
    cursor.execute(f'select * from Data where question_opening=0 and user_id="{call.message.chat.id}"')
    x = cursor.fetchall()
    connection.commit()

    connection.close()

    result_opened = ''
    counter_opened = 0

    if len(x) != 0:
        for el1 in x:
            result_opened += f'#{el1[0]}: <b>"{el1[6]}"</b>\nДата и время: {el1[4]} {el1[5]}'
            if counter_opened < len(x):
                result_opened += '\n\n'
                counter_opened += 1
            elif counter_opened == len(x) or len(x) == 1:
                pass

        await call.message.edit_text(text=f'''{result_opened}''', parse_mode="HTML", reply_markup=types.InlineKeyboardMarkup(row_width=2).add(types.InlineKeyboardButton(text='Открытые', callback_data='opened_questions_show')).insert(types.InlineKeyboardButton(text='Закрытые', callback_data='closed_questions_show')).add(types.InlineKeyboardButton(text='Все вопросы', callback_data='all_my_questions')))
    else:
        await call.answer(text='У вас нет открытых вопросов!', show_alert=True)

@dp.callback_query_handler(text='closed_questions_show')
async def show_closed_questions(call: types.CallbackQuery):
    connection = sqlite3.connect('Resources/Data/DataBase.db')
    cursor = connection.cursor()
    cursor.execute(f'select * from Data where question_opening=1 and user_id="{call.message.chat.id}"')
    x = cursor.fetchall()
    connection.commit()

    connection.close()

    result_closed = ''
    counter_closed = 0

    if len(x) != 0:
        for el1 in x:
            result_closed += f'#{el1[0]}: <b>"{el1[6]}"</b>\nДата и время: {el1[4]} {el1[5]}\nОтвет Разработчика: "{el1[8]}"'
            if counter_closed < len(x):
                result_closed += '\n\n'
                counter_closed += 1
            elif counter_closed == len(x) or len(x) == 1:
                pass

        await call.message.edit_text(text=f'''{result_closed}''', parse_mode="HTML",
                                     reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                         types.InlineKeyboardButton(text='Открытые',
                                                                    callback_data='opened_questions_show')).insert(
                                         types.InlineKeyboardButton(text='Закрытые',
                                                                    callback_data='closed_questions_show')).add(
                                         types.InlineKeyboardButton(text='Все вопросы', callback_data='all_my_questions')))
    else:
        await call.answer(text='У вас нет закрытых вопросов!', show_alert=True)


@dp.callback_query_handler(text='all_my_ideas')
async def all_my_questions_func(call: types.CallbackQuery):
    connection = sqlite3.connect('Resources/Data/DataBase.db')
    cursor = connection.cursor()
    cursor.execute(f'select * from Ideas where user_id="{call.message.chat.id}"')
    fetch = cursor.fetchall()
    connection.commit()
    connection.close()

    result = ''
    counter = 0
    for el in fetch:
        result += f'''{counter + 1}. Идея: <b>"{el[6]}"</b>\nДата и время: {el[4]} {el[5]}\nСтатус рассмотрения: '''

        if el[7] == 0:
            result += f'{hbold("Не рассмотрена")}'
        elif el[7] == 1:
            result += f'{hbold("Принята к сведению")}'
        elif el[7] == 2:
            result += f'{hbold("Отклонена")}'

        if counter < (len(fetch) - 1):
            result += '\n\n'
            counter += 1
        elif counter == len(fetch) or len(fetch) == 1:
            pass

    await call.message.answer(text=f'''{hbold(f"Всего предложенных вами идей — {len(fetch)}:")}\n\n{result}''',
                         protect_content=True, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                         types.InlineKeyboardButton(text='Не рассмотренные',
                                                                    callback_data='not_checked_ideas_show')).insert(
                                         types.InlineKeyboardButton(text='Принятые',
                                                                    callback_data='accepted_ideas_show')).add(
                                         types.InlineKeyboardButton(text='Отклоненные',
                                                                    callback_data='rejected_ideas_show')))

@dp.callback_query_handler(text='not_checked_ideas_show')
async def show_opened_questions(call: types.CallbackQuery):
    connection = sqlite3.connect('Resources/Data/DataBase.db')
    cursor = connection.cursor()
    cursor.execute(f'select * from Ideas where idea_accepted=0 and user_id="{call.message.chat.id}"')
    x = cursor.fetchall()
    connection.commit()
    connection.close()

    result = ''
    counter = 0

    if len(x) != 0:
        for el in x:
            result += f'''{counter + 1}. Идея: <b>"{el[6]}"</b>\nДата и время: {el[4]} {el[5]}'''

            if counter < (len(x) - 1):
                result += '\n\n'
                counter += 1
            elif counter == len(x) or len(x) == 1:
                pass

        await call.message.edit_text(text=f'''{result}''', parse_mode="HTML",
                                     reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                         types.InlineKeyboardButton(text='Не рассмотренные',
                                                                    callback_data='not_checked_ideas_show')).insert(
                                         types.InlineKeyboardButton(text='Принятые',
                                                                    callback_data='accepted_ideas_show')).add(
                                         types.InlineKeyboardButton(text='Отклоненные',
                                                                    callback_data='rejected_ideas_show')).add(
                                         types.InlineKeyboardButton(text='Все идеи', callback_data='all_my_ideas')))
    else:
        await call.answer(text='У вас нет не рассмотренных идей!', show_alert=True)

@dp.callback_query_handler(text='accepted_ideas_show')
async def show_closed_questions(call: types.CallbackQuery):
    connection = sqlite3.connect('Resources/Data/DataBase.db')
    cursor = connection.cursor()
    cursor.execute(f'select * from Ideas where idea_accepted=1 and user_id="{call.message.chat.id}"')
    x = cursor.fetchall()
    connection.commit()
    connection.close()

    result = ''
    counter = 0

    if len(x) != 0:
        for el in x:
            result += f'''{counter + 1}. Идея: <b>"{el[6]}"</b>\nДата и время: {el[4]} {el[5]}'''

            if counter < (len(x) - 1):
                result += '\n\n'
                counter += 1
            elif counter == len(x) or len(x) == 1:
                pass

        await call.message.edit_text(text=f'''{result}''', parse_mode="HTML",
                                     reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                         types.InlineKeyboardButton(text='Не рассмотренные',
                                                                    callback_data='not_checked_ideas_show')).insert(
                                         types.InlineKeyboardButton(text='Принятые',
                                                                    callback_data='accepted_ideas_show')).add(
                                         types.InlineKeyboardButton(text='Отклоненные', callback_data='rejected_ideas_show')).add(
                                         types.InlineKeyboardButton(text='Все идеи', callback_data='all_my_ideas')))
    else:
        await call.answer(text='У вас нет принятых идей!', show_alert=True)

@dp.callback_query_handler(text='rejected_ideas_show')
async def show_closed_questions(call: types.CallbackQuery):
    connection = sqlite3.connect('Resources/Data/DataBase.db')
    cursor = connection.cursor()
    cursor.execute(f'select * from Ideas where idea_accepted=2 and user_id="{call.message.chat.id}"')
    x = cursor.fetchall()
    connection.commit()
    connection.close()

    result = ''
    counter = 0

    if len(x) != 0:
        for el in x:
            result += f'''{counter + 1}. Идея: <b>"{el[6]}"</b>\nДата и время: {el[4]} {el[5]}'''

            if counter < (len(x) - 1):
                result += '\n\n'
                counter += 1
            elif counter == len(x) or len(x) == 1:
                pass

        await call.message.edit_text(text=f'''{result}''', parse_mode="HTML",
                                     reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                                         types.InlineKeyboardButton(text='Не рассмотренные',
                                                                    callback_data='not_checked_ideas_show')).insert(
                                         types.InlineKeyboardButton(text='Принятые',
                                                                    callback_data='accepted_ideas_show')).add(
                                         types.InlineKeyboardButton(text='Отклоненные', callback_data='rejected_ideas_show')).add(
                                         types.InlineKeyboardButton(text='Все идеи', callback_data='all_my_ideas')))
    else:
        await call.answer(text='У вас нет отклоненных идей!', show_alert=True)


@dp.callback_query_handler(text='how_this_bot_works')
async def how_bot_works(call: types.CallbackQuery):
    await call.message.edit_caption(
        caption=texts.htbws_support_text,
        reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton(text="Как работает бот", callback_data="how_this_bot_works"),
            types.InlineKeyboardButton(text="Как поинтересоваться", callback_data="how_do_question"),
            types.InlineKeyboardButton(text="На главную", callback_data="start_call")
        ),
        parse_mode='HTML'
    )

@dp.callback_query_handler(text='how_do_question')
async def how_bot_works(call: types.CallbackQuery):
    await call.message.edit_caption(
        caption=texts.hdq_support_text,
        reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton(text="Как работает бот", callback_data="how_this_bot_works"),
            types.InlineKeyboardButton(text="Как поинтересоваться", callback_data="how_do_question"),
            types.InlineKeyboardButton(text="На главную", callback_data="start_call")
        ),
        parse_mode='HTML'
    )

@dp.callback_query_handler(text='close_question')
async def understood_close_message(call: types.CallbackQuery):
    question_heading = (call.message.text).split('"', 1)[1].split('"')[0]
    question_answer = (call.message.text).split(' поступил ответ:\n\n', 1)[1]

    connection = sqlite3.connect('Resources/Data/DataBase.db')
    cursor = connection.cursor()
    cursor.execute(f'update Data set question_opening=1 where question_heading="{question_heading}" and question_answer="{question_answer}"')
    connection.commit()
    connection.close()

    await call.answer(text='''Ваш вопрос был успешно закрыт!''')

@dp.callback_query_handler(text='understood')
async def understood_close_message(call: types.CallbackQuery):
    await call.message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, fast=True)
