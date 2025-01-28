from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from aiogram.utils.markdown import hcode, hbold, hitalic

from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.deep_linking import decode_payload

import re

import pymysql
from pymysql import cursors
from datetime import datetime

import texts
import config


API_TOKEN = config.API_TOKEN_TEST

db_host = config.db_host
db_user = config.db_user
db_database = config.db_database
db_port = config.db_port
db_password = config.db_password


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(text='Привет, это тестовый бот.\nЗапусти тестовую версию Web-приложения FreeIvannikovCoin:', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text='Открыть', web_app=types.WebAppInfo(url=f'https://student-projects.anosoff.com/ec883370694191262ca4364fb7b34135e11947b8/FIC-WebApp/index.html?user_id={message.chat.id}'))))


@dp.callback_query_handler(text='understood')
async def understood_close_message(call: types.CallbackQuery):
    await call.message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, fast=True)