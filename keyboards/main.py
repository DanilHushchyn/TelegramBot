from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __


def get_main_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("🗂 Список объявлений"))
    kb.button(text=_("➕ Создать объявление"))
    kb.button(text=_("👤 Мой профиль"))
    kb.button(text=_("🚪 Выход"))
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_bc_kb():
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text=_("Назад")),
        KeyboardButton(text=_("Отмена")),
    )
    return kb.as_markup(resize_keyboard=True)
