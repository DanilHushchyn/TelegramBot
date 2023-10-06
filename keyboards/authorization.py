from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_language_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Русский")
    kb.button(text="English")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_authorization_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Вход")
    kb.button(text="Регистрация")
    kb.button(text="Выбор языка")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_register_keyboard():
    buttons = [
        [
            types.KeyboardButton(text=str("Зарегистрироваться"))
        ],
        [
            types.KeyboardButton(text=str("Редактировать email")),
            types.KeyboardButton(text=str("Редактировать пароль"))
        ],
        [
            types.KeyboardButton(text=str("Редактировать имя")),
            types.KeyboardButton(text=str("Редактировать фамилию")),
        ],
        [
            types.KeyboardButton(text=str('Отмена'))
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard


def get_back_register():
    buttons = [
        [
            types.KeyboardButton(text=str('Вернутся к регистрации'))
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard