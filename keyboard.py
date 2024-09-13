from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard() -> InlineKeyboardMarkup:
    button1 = InlineKeyboardButton(text='Добавить альбом', callback_data='album_info')
    button2 = InlineKeyboardButton(text='Мои альбомы', callback_data='my_albums')
    button3 = InlineKeyboardButton(text='Удалить альбом', callback_data='delete_album')
    kb = InlineKeyboardMarkup(inline_keyboard=[[button1], [button2], [button3]])
    return kb


def delete_album_keyboard() -> InlineKeyboardMarkup:
    button_back = InlineKeyboardButton(text='Назад', callback_data='back_to_start')
    kb = InlineKeyboardMarkup(inline_keyboard=[[button_back]])
    return kb


def album_info_keyboard() -> InlineKeyboardMarkup:
    button1 = InlineKeyboardButton(text='Название альбома', callback_data='album_title')
    button2 = InlineKeyboardButton(text='Пароль', callback_data='album_password')
    button3 = InlineKeyboardButton(text='Автоудаление', callback_data='album_autodelete')
    button4 = InlineKeyboardButton(text='Загрузить фотографии', callback_data='add_album')
    button_back = InlineKeyboardButton(text='Назад', callback_data='back_to_start')
    kb = InlineKeyboardMarkup(inline_keyboard=[[button1], [button2, button3], [button4], [button_back]])
    return kb


def album_autodelete_keyboard() -> InlineKeyboardMarkup:
    button1 = InlineKeyboardButton(text='День', callback_data='1day')
    button2 = InlineKeyboardButton(text='Неделя', callback_data='1week')
    button3 = InlineKeyboardButton(text='Месяц', callback_data='1month')
    button4 = InlineKeyboardButton(text='Год', callback_data='1year')
    button5 = InlineKeyboardButton(text='Никогда', callback_data='never')
    button_back = InlineKeyboardButton(text='Назад', callback_data='back_to_album_info')
    kb = InlineKeyboardMarkup(inline_keyboard=[[button1, button2], [button3, button4], [button5], [button_back]])
    return kb


def back_keyboard() -> InlineKeyboardMarkup:
    button_back = InlineKeyboardButton(text='Назад', callback_data='back_to_album_info')
    kb = InlineKeyboardMarkup(inline_keyboard=[[button_back]])
    return kb


def stop_loading_keyboard() -> InlineKeyboardMarkup:
    button1 = InlineKeyboardButton(text='Завершить загрузку', callback_data='stop_loading')
    kb = InlineKeyboardMarkup(inline_keyboard=[[button1]])
    return kb
