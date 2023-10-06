from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🗂 Список объявлений")
    kb.button(text="➕ Создать объявление")
    kb.button(text="👤 Мой профиль")
    kb.button(text="⚙️ Русский/English")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
