from config import BOT_TOCEN
from functions import *

import requests

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

storage = MemoryStorage()
bot = Bot(BOT_TOCEN)
dp = Dispatcher(bot, storage=storage)


class CreateQRCode(StatesGroup):
    get_text = State()


class Settings(StatesGroup):
    size = State()
    qzone = State()
    margin = State()
    ecc = State()
    color = State()
    bgcolor = State()


def get_keyboard_for_start() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/qr_code"), KeyboardButton("/settings"))
    return kb


def get_keyboard_for_settings() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Размер", callback_data="size"),
                                                 InlineKeyboardButton(text="Отступ", callback_data="qzone"),
                                                 InlineKeyboardButton(text="Поля", callback_data="margin")],
                                                [InlineKeyboardButton(text="ECC", callback_data="ecc"),
                                                 InlineKeyboardButton(text="Цвет", callback_data="color"),
                                                 InlineKeyboardButton(text="Цвет фона", callback_data="bgcolor")],
                                                [InlineKeyboardButton(text="Готово", callback_data="done")]])
    return ikb


@dp.message_handler(commands=["start"])
async def start(message: types.Message) -> None:
    await message.answer(
        text="Привет. Я бот для создания qr-кодов. Вот что я умею:\n/qr_code - создание qr-кода\n/settings - настройки",
        reply_markup=get_keyboard_for_start())
    create_settings(message)


@dp.message_handler(commands=["qr_code"])
async def start_generate_qr_code(message: types.Message) -> None:
    await message.answer(text="Введите текст qr-кода", reply_markup=ReplyKeyboardRemove())
    await CreateQRCode.get_text.set()


@dp.message_handler(state=CreateQRCode.get_text)
async def get_text_for_qr_code(message: types.Message, state: FSMContext) -> None:
    settings_dict = get_settings(message)
    settings_list = list(zip(settings_dict.keys(), settings_dict.values()))
    del settings_list[0]
    settings_list.append(("data", message.text))

    url = f'http://api.qrserver.com/v1/create-qr-code/?{"&".join(list(map(lambda x: f"{x[0]}={x[1]}", settings_list)))}'
    await bot.send_photo(chat_id=message.chat.id, photo=url, reply_markup=get_keyboard_for_start())
    await state.finish()


@dp.message_handler(commands=["settings"])
async def settings(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["menu"] = await message.answer(
            text="Нажмите на нужный пункт для полной информации и настройки.\nНастройки сохраняються сразу после изменения.",
            reply_markup=get_keyboard_for_settings())


async def go_to_menu(message: types.Message, state: FSMContext):
    await bot.edit_message_text(message_id=message.message_id, chat_id=message.chat.id,
                                text="Нажмите на нужный пункт для полной информации и настройки."
                                     "\nНастройки сохраняються сразу после изменения.",
                                reply_markup=get_keyboard_for_settings())
    await state.finish()


@dp.callback_query_handler()
async def settings_menu_callback_query(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "size":
        await bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                    text="Введите размер qr-кода в пикселях. 1 число - значение стороны квадрата. "
                                         "В диопазоне от 10 до 1000", )
        await Settings.size.set()


@dp.message_handler(lambda message: message.text.isalnum(), state=Settings.size)
async def get_size(message: types.Message, state: FSMContext):
    n = int(message.text)
    if 10 <= n <= 1000:
        update_settings(message, "size", n)
        await message.delete()

        async with state.proxy() as data:
            await go_to_menu(data["menu"], state)



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
