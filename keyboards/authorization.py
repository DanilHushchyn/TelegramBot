from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def get_language_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Русский")
    kb.button(text="English")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_authorization_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Вход"))
    kb.button(text=_("Регистрация"))
    kb.button(text=_("Выбор языка"))
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_register_keyboard():
    buttons = [
        [
            types.KeyboardButton(text=str(_("Зарегистрироваться")))
        ],
        [
            types.KeyboardButton(text=str(_("Редактировать email"))),
            types.KeyboardButton(text=str(_("Редактировать пароль")))
        ],
        [
            types.KeyboardButton(text=str(_("Редактировать имя"))),
            types.KeyboardButton(text=str(_("Редактировать фамилию"))),
        ],
        [
            types.KeyboardButton(text=str(_('Отмена')))
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
            types.KeyboardButton(text=str(_('Вернутся к регистрации')))
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard