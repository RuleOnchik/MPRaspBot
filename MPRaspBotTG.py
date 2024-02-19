from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import FSInputFile
from aiogram.utils import media_group
from aiogram import types, F, Router
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import datetime
import time
import os
import sys

sys.path.append('C:\\Users\\truel\\AppData\\Local\\Programs\\Python')

# from MyMods.ERP import ShablonReply as sr
# from MyMods.ERP import SimpleFunks as smf
from MyMods.ERP import SimpleParams as smp
# from MyMods.ERP import AnalysePack as ap
from MyMods.ERP import SeleniumPack as sp

import raspisanie


TODAY = smp.Today()

all_start_time = time.time()
print("Начало работы: ", TODAY.dat)
print()

Token = "5398655186:AAFX8QtPItIo6pjCSaFBc4Oq-Rh1gbZFVOU"

bot = Bot(token=Token, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)
print("Запущен")

class Form_logs(StatesGroup):
    make_log = State()

class Form_weekday(StatesGroup):
    weekday = State()


reply_markup_start = ReplyKeyboardMarkup(
        keyboard=[[
                KeyboardButton(text="Сейчас"),
                KeyboardButton(text="Расписание"),
                KeyboardButton(text="Задать группу"),
            ]],
        resize_keyboard=True,)

reply_markup_weekdays = ReplyKeyboardMarkup(
        keyboard=[[
                KeyboardButton(text="Понедельник"),
                KeyboardButton(text="Вторник"),
                KeyboardButton(text="Среда"),
                ],
                [
                KeyboardButton(text="Четверг"),
                KeyboardButton(text="Пятница"),
                KeyboardButton(text="Суббота"),
                ],
                [
                KeyboardButton(text="Отмена"),
            ]],
        resize_keyboard=True,)


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext) -> None:
    #Этот блок создан для логирования. При основном использовании можно удалить
    # {
    # logging(message)
    print("step: start")
    print("chat id:", message.chat.id)
    print("user id:", message.from_user.id)
    print("user name:", message.from_user.first_name)
    # }

    # await state.set_state(Form_mode.mode)

    await message.answer(f"Привет, {message.from_user.first_name}!\nВыбери что тебе нужно из списка и тогда поговорим дальше)\n\nЕсли ты впервый раз, то обязательно сначала задай группу!", reply_markup=reply_markup_start)
    # await message.answer("Привет! Отправь мне файл выгрузки и я через время отправлю тебе Итоговый отчет!")

@router.message(F.text.casefold() == "отмена")
async def rasp_now(message: Message, state: FSMContext) -> None:
    # await state.clear()
    # {
    print("step: Отмена")
    print("chat id:", message.chat.id)
    print("user id:", message.from_user.id)
    print("user name:", message.from_user.first_name)
    # }

    await state.clear()
    # await state.set_state(Form_mode.mode)

    await message.answer(f"Отмена", reply_markup=reply_markup_start)


@router.message(F.text.casefold() == "сейчас")
async def rasp_now(message: Message, state: FSMContext) -> None:
    # await state.clear()
    # {
    print("step: Сейчас")
    print("chat id:", message.chat.id)
    print("user id:", message.from_user.id)
    print("user name:", message.from_user.first_name)
    # }

    try:
        answer_text, link = raspisanie.now_schedule(message.chat.id, "Telegram")
    except Exception as error:
        answer_text = str(error)
        link = None
    if link:
        inline_markup = InlineKeyboardMarkup(
                inline_keyboard=[[
                        InlineKeyboardButton(text=link[0][0], url=link[0][1]),
                    ]])
    else:
        inline_markup = None
    await message.answer(answer_text, reply_markup=inline_markup)

@router.message(F.text.casefold() == "расписание")
async def rasp_weekday(message: Message, state: FSMContext) -> None:
    # await state.clear()
    # {
    print("step: Расписание")
    print("chat id:", message.chat.id)
    print("user id:", message.from_user.id)
    print("user name:", message.from_user.first_name)
    # }

    await state.set_state(Form_weekday.weekday)
    await message.answer(f"Какой день интересует?)", reply_markup=reply_markup_weekdays)

@router.message(Form_weekday.weekday)
async def weekday(message: Message, state: FSMContext) -> None:
    # await state.clear()
    # {
    print("step:", message.text)
    print("chat id:", message.chat.id)
    print("user id:", message.from_user.id)
    print("user name:", message.from_user.first_name)
    # }

    try:
        answer_text, links = raspisanie.day_schedule(message.text, message.chat.id, "Telegram")
    except Exception as error:
        answer_text = str(error)
        links = None
    if links:
        inline_keyboard = []
        for text, link in links:
            inline_keyboard.append([InlineKeyboardButton(text=text, url=link)])
        inline_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    else:
        inline_markup = None
    await message.answer(answer_text, reply_markup=inline_markup)



@router.message(F.text.casefold() == "задать группу")
async def rasp_weekday(message: Message, state: FSMContext) -> None:
    # await state.clear()
    # {
    print("step: Задать группу")
    print("chat id:", message.chat.id)
    print("user id:", message.from_user.id)
    print("user name:", message.from_user.first_name)
    # }

    await state.set_state(Form_logs.make_log)
    # await state.set_state(Form_weekday.weekday)
    await message.answer(f"Напиши мне свою группу!\nЕсли что формат должен быть такой:\n\n Группа: XXX-XXX\nили\n XXX-XXX\n\nгде XXX-XXX - номер твоей группы")

@router.message(Form_logs.make_log)
async def monday(message: Message, state: FSMContext) -> None:
    # await state.clear()
    # {
    print("step: Задать группу обработка")
    print("chat id:", message.chat.id)
    print("user id:", message.from_user.id)
    print("user name:", message.from_user.first_name)
    # }

    await state.clear()
    await message.answer(raspisanie.make_log_json(message.text, message.chat.id, "Telegram"), reply_markup=reply_markup_start)


@router.message()
async def mes_handle(message: Message, state: FSMContext) -> None:
    # {
    print("step: Просто сообщение")
    print("chat id:", message.chat.id)
    print("user id:", message.from_user.id)
    print("user name:", message.from_user.first_name)
    # }

    await message.answer("Если не работает, попробуй нажать \"Отмена\"")

if __name__ == '__main__':
    dp.run_polling(bot, allowed_updates=dp.resolve_used_update_types())
