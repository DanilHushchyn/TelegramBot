import httpx
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.main_callbacks import CoordinateCallbackFactory, GalleryCallbackFactory
from keyboards.main import get_main_kb

router = Router()


async def cmd_start(message: types.Message):
    await message.answer("Главное меню: ", reply_markup=get_main_kb())




@router.message(F.text == '👤 Мой профиль')
async def my_profile(message: Message):
    resp = httpx.post('http://127.0.0.0:8000/api/v1/auth/login/', data={
        "email": "badegox807@tipent.com",
        "password": "sword123"
    })
    headers = {
        "Authorization": f"Bearer {resp.json()['access']}"
    }
    resp = httpx.get('http://127.0.0.0:8000/api/v1/auth/profiles/my_profile/', headers=headers)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="📑 Список моих объявлений",
        callback_data="my_announcements")
    )
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    await message.answer_photo(
        image_from_url,
        caption=
        f"<b>Мой Аккаунт:</b>\n"
        f"<b>Фамилия:</b> {resp.json()['last_name']}\n"
        f"<b>Имя:</b> {resp.json()['first_name']}\n"
        f"<b>Email:</b> {resp.json()['email']}\n"
        f"<b>Телефон:</b> {resp.json()['phone']}\n\n"
        f"👥 <b>Контакты агента</b> \n"
        f"Фамилия: {resp.json()['agent_contacts']['last_name']}\n"
        f"Имя: {resp.json()['agent_contacts']['first_name']}\n"
        f"Email: {resp.json()['agent_contacts']['email']}\n"
        f"Телефон: {resp.json()['agent_contacts']['phone']}\n",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "my_announcements")
async def my_announcements(callback: types.CallbackQuery):
    resp = httpx.post('http://127.0.0.0:8000/api/v1/auth/login/', data={
        "email": "badegox807@tipent.com",
        "password": "sword123"
    })
    headers = {
        "Authorization": f"Bearer {resp.json()['access']}"
    }
    resp = httpx.get('http://127.0.0.0:8000/api/v1/client/announcements/my_announcements/', headers=headers)
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    for item in resp.json():
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Получить геопозицию",
            callback_data=CoordinateCallbackFactory(longtitude=float(item['map_lon']),
                                                    latitude=float(item['map_lat'])).pack()
        ))
        builder.add(types.InlineKeyboardButton(
            text="Просмотреть галерею",
            callback_data=GalleryCallbackFactory(id=item['id']).pack()
        ))

        await callback.message.answer_photo(
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
            reply_markup=builder.as_markup()

        )

        # Send the media group
        # await callback.bot.send_media_group(chat_id=callback.message.chat.id, media=media)


@router.callback_query(CoordinateCallbackFactory.filter())
async def get_location(callback: types.CallbackQuery, callback_data: CoordinateCallbackFactory):
    # Obtenez les coordonnées de longitude et de latitude
    # Utilisez la méthode sendLocation pour envoyer la géolocalisation
    await callback.bot.send_location(chat_id=callback.message.chat.id, latitude=callback_data.latitude,
                                     longitude=callback_data.longtitude)
    await callback.answer(
        text="",
    )


@router.callback_query(GalleryCallbackFactory.filter())
async def show_gallery(callback: types.CallbackQuery, callback_data: CoordinateCallbackFactory):
    print(callback_data.id)  # По id запросишь объвление и вытащишь тут галерею для отображения
    gallery = [
        "https://picsum.photos/seed/groosha/400/300",
        "https://picsum.photos/seed/groosha/400/300",
        "https://picsum.photos/seed/groosha/400/300",
    ]

    # Create a list of InputMediaPhoto objects
    media = [types.InputMediaPhoto(media=photo) for photo in gallery]
    await callback.bot.send_media_group(chat_id=callback.message.chat.id, media=media)
    await callback.answer(
        text="",
    )
