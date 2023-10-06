from aiogram import types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_pagination_keyboard(page_num: int, next: int, prev: int):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="←",
        callback_data=f"previous_{prev}")
    )
    builder.add(types.InlineKeyboardButton(
        text="→",
        callback_data=f"next_{next}")
    )
    builder.row(types.InlineKeyboardButton(
        text=f"1/{page_num}",
        callback_data="page_button"),
    )
    return builder.as_markup(resize_keyboard=True)

