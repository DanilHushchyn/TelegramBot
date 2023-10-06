from aiogram.fsm.state import StatesGroup, State


class Start(StatesGroup):
    language = State()
    login_or_register = State()


class Login(StatesGroup):
    email = State()
    password = State()
    complete = State()


class Register(StatesGroup):
    first_name = State()
    edit_first_name = State()
    last_name = State()
    edit_last_name = State()
    email = State()
    edit_email = State()
    password = State()
    edit_password = State()
    complete = State()
