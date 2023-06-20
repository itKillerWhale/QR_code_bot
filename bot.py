from config import BOT_TOCEN
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


def get_markup_for_start() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/qr_code"), KeyboardButton("/settings"))
    return kb


@dp.message_handler(commands=["start"])
async def start(message: types.Message) -> None:
    await message.answer(
        text="Привет. Я бот для создания qr-кодов. Вот что я умею:\n/qr_code - создание qr-кода\n/settings - настройки",
        reply_markup=get_markup_for_start())


@dp.message_handler(commands=["qr_code"])
async def start_generate_qr_code(message: types.Message) -> None:
    await message.answer(text="Введите текст qr-кода", reply_markup=ReplyKeyboardRemove())
    await CreateQRCode.get_text.set()


@dp.message_handler(state=CreateQRCode.get_text)
async def get_text_for_qr_code(message: types.Message, state: FSMContext) -> None:
    url = f'http://api.qrserver.com/v1/create-qr-code/?data={message.text}'
    await bot.send_photo(chat_id=message.chat.id, photo=url, reply_markup=get_markup_for_start())
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
