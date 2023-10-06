import httpx
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks.main_callbacks import CoordinateCallbackFactory, GalleryCallbackFactory
from keyboards.main import get_main_kb
from keyboards.pagination import get_pagination_keyboard
from test_lessons import dp

router = Router()  # [1]


@router.message(F.text == '🗂 Список объявлений')
async def all_announcements(message: Message, page_num=0):
    resp = httpx.post('http://127.0.0.0:8000/api/v1/auth/login/', data={
        "email": "badegox807@tipent.com",
        "password": "sword123"
    })
    headers = {
        "Authorization": f"Bearer {resp.json()['access']}"
    }
    resp = httpx.get('http://127.0.0.0:8000/api/v1/client/announcements/', headers=headers)
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    if page_num + 1 > len(resp.json()):
        page_num = 0
    elif page_num + 1 <= 0:
        page_num = len(resp.json()) - 1
    item = resp.json()[page_num]

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="←",
        callback_data=f"previous_{page_num - 1}")
    )
    builder.add(types.InlineKeyboardButton(
        text=f"{page_num + 1}/{len(resp.json())}",
        callback_data="page_button")
    )
    builder.add(types.InlineKeyboardButton(
        text="→",
        callback_data=f"next_{page_num + 1}")
    )

    builder.row(types.InlineKeyboardButton(
        text="Получить геопозицию",
        callback_data=CoordinateCallbackFactory(longtitude=float(item['map_lon']),
                                                latitude=float(item['map_lat'])).pack()
    ),
        types.InlineKeyboardButton(
            text="Просмотреть галерею",
            callback_data=GalleryCallbackFactory(id=item['id']).pack()
        )
    )

    await message.answer_photo(
        image_from_url,
        caption=
        f"<b>Адрес:</b> {item['description']}\n"
        f"<b>Актуально:</b> {'ДА' if item['is_actual'] else 'НЕТ'}\n"
        f"<b>Модерация:</b> {'Пройдена' if item['is_moderated'] else 'Не пройдена'}\n"
        f"<b>Статус модерации:</b> {item['moderation_status'] if item['moderation_status'] else '...'}\n"
        f"<b>Документ основания:</b> {item['grounds_doc']}\n"
        f"<b>Назначение:</b> {item['appointment']}\n"
        f"<b>Количество комнат:</b> {item['room_count']}\n"
        f"<b>Планировка:</b> {item['layout']}\n"
        f"<b>Жилое состояние:</b> {item['living_condition']}\n"
        f"<b>Общая площадь:</b> {item['square']}\n"
        f"<b>Площадь кухни:</b> {item['kitchen_square']}\n"
        f"<b>Балкон/лоджия:</b> {item['balcony_or_loggia']}\n"
        f"<b>Тип отопления:</b> {item['heating_type']}\n"
        f"<b>Варианты расчета:</b> {item['payment_type']}\n"
        f"<b>Коммисия агенту:</b> {item['agent_commission']}\n"
        f"<b>Способ связи:</b> {item['communication_type']}\n"
        f"<b>Описание:</b> {item['description']}\n"
        f"<b>Цена:</b> {item['price']}\n",
        parse_mode="HTML",
        reply_markup=builder.as_markup(resize_keyboard=True)

    )


@router.callback_query(F.data.startswith("next_"))
async def callbacks_num(callback: types.CallbackQuery):
    number = callback.data.split('_')[1]
    await all_announcements(callback.message, int(number))
    await callback.answer()


@router.callback_query(F.data.startswith("previous_"))
async def callbacks_num(callback: types.CallbackQuery):
    number = callback.data.split('_')[1]
    await all_announcements(callback.message, int(number))
    await callback.answer()
