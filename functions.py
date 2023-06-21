import sqlite3
from aiogram import types


def create_settings(message: types.Message) -> None:
    with sqlite3.connect('db/data.db') as con:
        cursor = con.cursor()
        results = cursor.execute(
            f"""INSERT INTO settings VALUES({message.from_user.id}, {200}, 'L', '(0,0,0)', '(255,255,255)', 0, 10)""").fetchall()


def get_settings(message: types.Message) -> dict:
    with sqlite3.connect('db/data.db') as con:
        cursor = con.cursor()
        results = cursor.execute(f"""SELECT * FROM settings WHERE user_id = {message.from_user.id}""").fetchall()[0]
        print(results)

    print(results[3])
    settings_dict = {"user_id": results[0],
                     "size": f"{results[1]}x{results[1]}",
                     "ecc": results[2],
                     "color": results[3],
                     "bgcolor": results[4],
                     "margin": results[5],
                     "qzone": results[6]}

    return settings_dict
