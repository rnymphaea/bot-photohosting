from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    login = State()
    interaction = State()
    add_album = State()
    delete_album = State()
    set_name_album = State()
    set_password_album = State()
    set_autodelete_album = State()
