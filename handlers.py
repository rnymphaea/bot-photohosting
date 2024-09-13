import os

import requests

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message


from keyboard import main_keyboard, stop_loading_keyboard, album_info_keyboard, album_autodelete_keyboard, back_keyboard, delete_album_keyboard
from user_state import UserState
from bot import bot, SERVER_URL, TOKEN
from storage import jwt, tmp_files, album_data

router = Router()


@router.message(CommandStart())
async def on_start(message, state):
    await state.set_state(UserState.login)
    await message.answer(text="Приветствую вас!\nВведите ваш логин и пароль через пробел.")


@router.message(UserState.login)
async def login(message, state):
    try:
        username, password = message.text.split()
        data = {"username": username, "password": password}
        response = requests.post(SERVER_URL + "/login", json=data)
        print(response.status_code)
        if response.status_code == 200:
            print(response.json())
            jwt[message.from_user.id] = response.json()
            print(jwt[message.from_user.id])
            await state.set_state(UserState.interaction)

            kb = main_keyboard()
            await message.answer(text="Выберите действие:", reply_markup=kb)
        else:
            raise Exception("Incorrect username or password")
    except Exception as e:
        print(e)
        await message.answer("Некорректные данные")


@router.callback_query(lambda query: query.data == 'album_info')
async def album_info(query, state):
    kb = album_info_keyboard()
    await bot.answer_callback_query(query.id)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text="Введите опциональные поля / загрузите фотографии",
        reply_markup=kb
    )


@router.callback_query(lambda query: query.data == 'add_album')
async def add_album(query, state):
    kb = stop_loading_keyboard()

    await state.set_state(UserState.add_album)
    await bot.answer_callback_query(query.id)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text="Добавьте фотографии.\nКогда вы загрузите всё, что хотели, нажмите на кнопку под этим сообщением.",
        reply_markup=kb
    )


@router.callback_query(lambda query: query.data == 'stop_loading')
async def stop_loading(query, state):
    await state.set_state(UserState.interaction)
    await bot.answer_callback_query(query.id)
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    user_id = query.from_user.id
    if user_id in tmp_files and tmp_files[user_id] and user_id in jwt:
        # data = {}
        headers = {'Authorization': 'Bearer ' + jwt.get(user_id)}
        files = [('attachments', (file_name, open(file_name, 'rb'))) for file_name in tmp_files[user_id]]
        optional = album_data.get(user_id)
        if not optional:
            optional = {}
        response = requests.post(SERVER_URL+"/albums", data=optional, files=files, headers=headers)  # data = {}
        print(response.status_code)
        print(response.json())
        if response.status_code == 201:
            await bot.send_message(chat_id=query.from_user.id, text=f"Фотографии успешно сохранены!\nВаша ссылка: {response.json()}")
            print("Trying to delete files from local storage")
            for i in tmp_files[user_id]:
                os.remove(i)
        elif response.status_code == 401:
            await bot.send_message(chat_id=query.from_user.id, text="Зайдите в аккаунт")
            await state.set_state(UserState.login)
        else:
            await bot.send_message(chat_id=query.from_user.id, text="Произошла ошибка при добавлении фотографий!")
        tmp_files.pop(user_id, None)
        if not album_data.get(user_id):
            album_data.pop(user_id, None)
    else:
        print("something went wrong")

    kb = main_keyboard()
    await bot.send_message(chat_id=query.from_user.id, text="Выберите действие:", reply_markup=kb)


@router.callback_query(lambda query: query.data == 'my_albums')
async def my_albums(query, state):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    user_id = query.from_user.id
    if user_id not in jwt:
        await bot.send_message(chat_id=user_id, text="Зайдите в аккаунт")
        await state.set_state(UserState.login)
    else:
        headers = {'Authorization': 'Bearer ' + jwt.get(user_id)}
        response = requests.get(SERVER_URL + "/albums", headers=headers)  # data = {}
        kb = main_keyboard()
        if response.status_code == 200:
            data = response.json()
            if data:
                message = ""
                for i in data:
                    message += f"Название альбома: {i['album_name']}\n"
                    message += f"Ссылка на альбом: {i['url']}\n"
                    message += f"Код альбома: `{i['code']}` \n"
                    message += "\n\n"
                await bot.send_message(user_id, text=message, parse_mode="markdown")
            else:
                await bot.send_message(user_id, text="У вас еще нет альбомов!")
            await bot.send_message(user_id, text="Выберите действие", reply_markup=kb)
            print(response.json())
        elif response.status_code == 401:
            await bot.send_message(chat_id=user_id, text="Зайдите в аккаунт")
            await state.set_state(UserState.login)
        else:
            await bot.send_message(chat_id=user_id, text="Произошла ошибка при получении альбомов")
            await bot.send_message(user_id, text="Выберите действие", reply_markup=kb)

        await bot.answer_callback_query(query.id)


@router.callback_query(lambda query: query.data == 'delete_album')
async def set_state_delete_album(query, state):
    print(query.data)
    if query.from_user.id not in jwt:
        await bot.send_message(query.from_user.id, text="Войдите в аккаунт")
        await state.set_state(UserState.login)
    else:
        await state.set_state(UserState.delete_album)
        kb = delete_album_keyboard()
        await bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text="Введите код альбома",
            reply_markup=kb,
        )
        # await bot.send_message(query.from_user.id, text=, reply_markup=kb)


@router.message(UserState.delete_album)
async def delete_album(message, state):
    user_id = message.from_user.id
    kb = main_keyboard()
    if user_id not in jwt:
        await bot.send_message(chat_id=user_id, text="Войдите в аккаунт")
        await state.set_state(UserState.login)
    else:
        headers = {'Authorization': 'Bearer ' + jwt.get(user_id)}
        data = {'code': str(message.text)}
        print(data)
        response = requests.post(SERVER_URL + "/albums/delete", headers=headers, json=data)  # data = {}
        print(response.status_code)
        if response.status_code == 204:
            await bot.send_message(user_id, text="Альбом успешно удалён!")
        else:
            await bot.send_message(user_id, text="Произошла ошибка при удалении альбома")
        await bot.send_message(user_id, text="Выберите действие", reply_markup=kb)


@router.message(F.photo, UserState.add_album)
async def handle_photo(message: Message):
    print("received photo")
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

    # Download the file
    response = requests.get(file_url)
    if response.status_code == 200:
        file_name = file_path.split('/')[-1]
        with open(file_name, 'wb') as f:
            f.write(response.content)
        if message.from_user.id not in tmp_files:
            tmp_files[message.from_user.id] = []
        tmp_files[message.from_user.id].append(file_name)

    await message.answer("Фото сохранено!")


@router.callback_query(lambda query: query.data == 'album_title')
async def set_state_title(query, state):
    kb = back_keyboard()
    await state.set_state(UserState.set_name_album)
    await bot.send_message(chat_id=query.from_user.id, text="Введите название альбома", reply_markup=kb)
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)


@router.message(UserState.set_name_album)
async def set_name_album(message, state):
    title = message.text
    user_id = message.from_user.id
    if not album_data.get(user_id):
        album_data[user_id] = {}
    album_data[user_id]["album_name"] = title
    kb = album_info_keyboard()
    print(album_data)
    await message.answer(text="Название альбома установлено")
    await message.answer(text="Введите опциональные поля / загрузите фотографии", reply_markup=kb)
    await state.set_state(UserState.interaction)


@router.callback_query(lambda query: query.data == 'album_password')
async def set_state_password(query, state):
    kb = back_keyboard()
    await state.set_state(UserState.set_password_album)
    await bot.send_message(chat_id=query.from_user.id, text="Введите пароль для альбома", reply_markup=kb)
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)


@router.message(UserState.set_password_album)
async def set_password_album(message, state):
    password = message.text
    user_id = message.from_user.id
    if not album_data.get(user_id):
        album_data[user_id] = {}
    album_data[user_id]["password"] = password
    kb = album_info_keyboard()
    print(album_data)
    await message.answer(text="Пароль альбома установлен")
    await message.answer(text="Введите опциональные поля", reply_markup=kb)
    await state.set_state(UserState.interaction)


@router.callback_query(lambda query: query.data == 'album_autodelete')
async def set_state_password(query, state):
    await state.set_state(UserState.set_autodelete_album)
    kb = album_autodelete_keyboard()
    await bot.send_message(chat_id=query.from_user.id, text="Выберите когда удалить альбом", reply_markup=kb)
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)


@router.callback_query(lambda query: query.data == 'back_to_start')
async def back(query, state):
    kb = main_keyboard()
    await state.set_state(UserState.interaction)
    await bot.answer_callback_query(query.id)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text="Выберите действие:",
        reply_markup=kb
    )


@router.callback_query(lambda query: query.data == 'back_to_album_info')
async def back(query, state):
    kb = album_info_keyboard()
    await state.set_state(UserState.interaction)
    await bot.answer_callback_query(query.id)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text="Введите опциональные поля / загрузите фотографии",
        reply_markup=kb
    )


@router.callback_query(lambda query: query.data in ['never', '1day', '1week', '1month', '1year'])
async def set_autodelete_album(query, state):
    user_id = query.from_user.id
    if not album_data.get(user_id):
        album_data[user_id] = {}
    album_data[user_id]["delete_at"] = query.data
    kb = album_info_keyboard()
    print(album_data)
    await bot.send_message(chat_id=query.from_user.id, text="Дата удаления альбома установлена")
    await bot.send_message(chat_id=query.from_user.id, text="Введите опциональные поля / загрузите фотографии", reply_markup=kb)
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await state.set_state(UserState.interaction)


@router.message(UserState.interaction)
async def handle_message(message):
    kb = main_keyboard()
    await message.answer(text="Выберите действие:", reply_markup=kb)
