import sqlite3
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot import go_to_menu


def create_settings(message: types.Message) -> None:
    with sqlite3.connect('db/data.db') as con:
        cursor = con.cursor()
        results = cursor.execute(
            f"""INSERT INTO settings VALUES({message.from_user.id}, {200}, 'L', '0-0-0', '255-255-255', 0, 10)""").fetchall()


def get_settings(user_id: int) -> dict:
    with sqlite3.connect('db/data.db') as con:
        cursor = con.cursor()
        results = cursor.execute(f"""SELECT * FROM settings WHERE user_id = {user_id}""").fetchall()[0]
        print(results)

    print(results[3])
    settings_dict = {"user_id": results[0],
                     "size": f"{results[1]}x{results[1]}",
                     "ecc": results[2],
                     "color": results[3],
                     "bgcolor": results[4],
                     "margin": results[5],
                     "qzone": results[6]}

    print(settings_dict)
    return settings_dict


def update_settings(user_id: int, settins_name: str, value) -> None:
    with sqlite3.connect('db/data.db') as con:
        # print("start")
        cursor = con.cursor()
        try:
            # print("try")
            value = int(value)

        except ValueError:
            # print("Except")
            cursor.execute(f"""UPDATE settings
                               SET {settins_name} = '{value}'
                               WHERE user_id = {user_id}""")

        else:
            # print("else")
            cursor.execute(f"""UPDATE settings
                               SET {settins_name} = {value}
                               WHERE user_id = {user_id}""")

        con.commit()


async def get_int(message: types.Message, state: FSMContext, borders, name: str):
    n = int(message.text)
    if borders(n):
        update_settings(message.from_user.id, name, n)
        await message.delete()

        async with state.proxy() as data:
            await go_to_menu(data["menu"], state)

    else:
        await message.delete()


async def get_callback(callback: types.CallbackQuery, state: FSMContext, name):

    update_settings(callback.from_user.id, name, callback.data)
    async with state.proxy() as data:
        await go_to_menu(data["menu"], state)
