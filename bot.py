import hashlib

from config import BOT_TOCEN
from functions import *

import requests

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto

storage = MemoryStorage()
bot = Bot(BOT_TOCEN)
dp = Dispatcher(bot, storage=storage)


class CreateQRCode(StatesGroup):
    get_text = State()


class Settings(StatesGroup):
    menu = State()

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


def get_keyboard_for_ecc() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Низкий (~7%)", callback_data="L")],
                                                [InlineKeyboardButton(text="Нормальный (~15%)", callback_data="M")],
                                                [InlineKeyboardButton(text="Средний (~25%)", callback_data="Q")],
                                                [InlineKeyboardButton(text="Большой (~30%)", callback_data="H")]])
    return ikb


def get_keyboard_for_color() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Черный", callback_data="0-0-0"),
                                                 InlineKeyboardButton(text="Белый", callback_data="255-255-255")],

                                                [InlineKeyboardButton(text="Крассный", callback_data="255-0-0"),
                                                 InlineKeyboardButton(text="Бардовый", callback_data="139-0-0")],

                                                [InlineKeyboardButton(text="Зелёный", callback_data="0-128-0"),
                                                 InlineKeyboardButton(text="Лаймовый", callback_data="0-255-0")],

                                                [InlineKeyboardButton(text="Жёлтый", callback_data="255-255-0"),
                                                 InlineKeyboardButton(text="Золотой", callback_data="255-215-0")],

                                                [InlineKeyboardButton(text="Голубой", callback_data="0-255-255"),
                                                 InlineKeyboardButton(text="Аквамарин",
                                                                      callback_data="127-255-212")],

                                                [InlineKeyboardButton(text="Синий", callback_data="0-0-255"),
                                                 InlineKeyboardButton(text="Индиго", callback_data="75-0-130")],

                                                [InlineKeyboardButton(text="Фиолетовый", callback_data="128-0-128"),
                                                 InlineKeyboardButton(text="Светло-фиолетовый",
                                                                      callback_data="148-0-211")]
                                                ])
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
    settings_dict = get_settings(message.from_user.id)
    print(settings_dict)
    settings_list = list(zip(settings_dict.keys(), settings_dict.values()))
    del settings_list[0]
    settings_list.append(("data", message.text))

    url = f'http://api.qrserver.com/v1/create-qr-code/?{"&".join(list(map(lambda x: f"{x[0]}={x[1]}", settings_list)))}'
    print(url)
    await bot.send_photo(chat_id=message.chat.id, photo=url, reply_markup=get_keyboard_for_start())
    await state.finish()


@dp.message_handler(commands=["settings"])
async def settings(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["menu"] = await message.answer(
            text="Нажмите на нужный пункт для полной информации и настройки."
                 "\nНастройки сохраняються сразу после изменения.",
            reply_markup=get_keyboard_for_settings())
    await message.delete()
    await Settings.menu.set()


async def go_to_menu(message: types.Message, state: FSMContext):
    await bot.edit_message_text(message_id=message.message_id, chat_id=message.chat.id,
                                text="Нажмите на нужный пункт для полной информации и настройки."
                                     "\nНастройки сохраняються сразу после изменения.",
                                reply_markup=get_keyboard_for_settings())
    await Settings.menu.set()


@dp.callback_query_handler(state=Settings.menu)
async def settings_menu_callback_query(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "size":
        await bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                    text="Размер qr-кода в пикселях. Число в диопазоне от 10 до 1000", )
        await Settings.size.set()

    elif callback.data == "margin":
        await bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                    text="Толщина поля в пикселях. Поля всегда будут иметь тот же цвет, что и фон "
                                         "(вы можете настроить это через bgcolor ). Он не будет добавляться к ширине"
                                         " изображения, заданной параметром size , поэтому он должен быть меньше, чем"
                                         " одна треть значения размера. Число в диопазоне от 0 до 50", )
        await Settings.margin.set()

    elif callback.data == "qzone":
        await bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                    text="Толщина поля («тихая зона», область без мешающих элементов, помогающая "
                                         "читателям найти QR-код) Тихая зона будет нарисована в дополнение к конечному"
                                         " установленному значению размера. Число в диопазоне от 0 до 100", )
        await Settings.qzone.set()

    elif callback.data == "ecc":
        await bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                    text="Код исправления ошибок (ECC), определяет степень избыточности"
                                         " данных. Чем выше избыточность данных, тем больше данных можно восстановить,"
                                         " если QR-код поврежден (например, царапины на наклейке с QR-кодом или что-то"
                                         " в этом роде).\nБолее высокий ECC приводит к сохранению большего количества "
                                         "данных и, следовательно, к QR-коду с большим количеством пикселей данных"
                                         " и большей матрицей данных. Самый низкий ECC является лучшим выбором для "
                                         "общих целей — устаревшие считыватели QR-кодов являются более распространенной"
                                         " проблемой, чем поврежденные QR-коды", reply_markup=get_keyboard_for_ecc())
        await Settings.ecc.set()

    elif callback.data == "color":
        await bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                    text="Код исправления ошибок (ECC), определяет степень избыточности"
                                         " данных. Чем выше избыточность данных, тем больше данных можно восстановить,"
                                         " если QR-код поврежден (например, царапины на наклейке с QR-кодом или что-то"
                                         " в этом роде).\nБолее высокий ECC приводит к сохранению большего количества "
                                         "данных и, следовательно, к QR-коду с большим количеством пикселей данных"
                                         " и большей матрицей данных. Самый низкий ECC является лучшим выбором для "
                                         "общих целей — устаревшие считыватели QR-кодов являются более распространенной"
                                         " проблемой, чем поврежденные QR-коды", reply_markup=get_keyboard_for_color())
        await Settings.color.set()
    elif callback.data == "bgcolor":
        await bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                    text="Код исправления ошибок (ECC), определяет степень избыточности"
                                         " данных. Чем выше избыточность данных, тем больше данных можно восстановить,"
                                         " если QR-код поврежден (например, царапины на наклейке с QR-кодом или что-то"
                                         " в этом роде).\nБолее высокий ECC приводит к сохранению большего количества "
                                         "данных и, следовательно, к QR-коду с большим количеством пикселей данных"
                                         " и большей матрицей данных. Самый низкий ECC является лучшим выбором для "
                                         "общих целей — устаревшие считыватели QR-кодов являются более распространенной"
                                         " проблемой, чем поврежденные QR-коды", reply_markup=get_keyboard_for_color())
        await Settings.bgcolor.set()
    elif callback.data == "done":
        await callback.message.delete()
        await state.finish()

@dp.message_handler(state=Settings.menu)
async def del_message(message: types.Message):
    await message.delete()


@dp.message_handler(lambda message: message.text.isalnum(), state=Settings.size)
async def get_size(message: types.Message, state: FSMContext):
    await get_int(message, state, lambda x: 10 <= x <= 1000, "size")


@dp.message_handler(lambda message: message.text.isalnum(), state=Settings.margin)
async def get_margin(message: types.Message, state: FSMContext):
    await get_int(message, state, lambda x: 0 <= x <= 50, "margin")


@dp.message_handler(lambda message: message.text.isalnum(), state=Settings.qzone)
async def get_qzone(message: types.Message, state: FSMContext):
    await get_int(message, state, lambda x: 0 <= x <= 100, "qzone")


@dp.callback_query_handler(state=Settings.ecc)
async def get_ecc(callback: types.CallbackQuery, state: FSMContext):
    await get_callback(callback, state, "ecc")


@dp.callback_query_handler(state=Settings.color)
async def get_ecc(callback: types.CallbackQuery, state: FSMContext):
    await get_callback(callback, state, "color")


@dp.callback_query_handler(state=Settings.bgcolor)
async def get_ecc(callback: types.CallbackQuery, state: FSMContext):
    await get_callback(callback, state, "bgcolor")


@dp.inline_handler()
async def iline_qr_code(inline_query: types.InlineQuery):
    text = inline_query.query or "IT_Fish"

    settings_dict = get_settings(inline_query.from_user.id)
    settings_list = list(zip(settings_dict.keys(), settings_dict.values()))
    del settings_list[0]
    settings_list.append(("data", text.replace(" ", "%20")))
    print(settings_list)

    url = f'http://api.qrserver.com/v1/create-qr-code/?{"&".join(list(map(lambda x: f"{x[0]}={x[1]}", settings_list)))}'
    print(url)

    result_id = hashlib.md5(url.encode()).hexdigest()

    item = InlineQueryResultPhoto(
        id=result_id,
        photo_url=url,
        thumb_url=url,
        photo_width=32,
        photo_height=32,
        )

    await bot.answer_inline_query(inline_query_id=inline_query.id, results=[item], cache_time=1)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
