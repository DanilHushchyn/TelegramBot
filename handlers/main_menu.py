from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.main_callbacks import CoordinateCallbackFactory, GalleryCallbackFactory
from keyboards.main import get_main_kb
from middlewares.auth import AuthMiddleware
import handlers.authorization as auth
from swipe_api.requests import UserAPIClient
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

router = Router()
router.message.middleware(AuthMiddleware())


async def cmd_start(message: types.Message):
    await message.answer(_("Главное меню: "), reply_markup=get_main_kb())


@router.message(F.text == __('🚪 Выход'))
async def logout_handler(message: types.Message, state: FSMContext):
    print('hello')
    client = UserAPIClient(user_id=message.chat.id)
    await client.logout()
    await state.clear()
    await auth.authorization_handler(message=message, state=state)


@router.message(F.text == __('👤 Мой профиль'))
async def my_profile(message: Message, state: FSMContext):
    client = UserAPIClient(user_id=message.chat.id)
    resp = await client.get_profile()
    if resp is None:
        await message.answer(text=_('Ваши данные устарели, нужно перезайти'))
        await logout_handler(message=message, state=state)
        return
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=_("📑 Список моих объявлений"),
        callback_data="my_announcements")
    )
    image_from_url = URLInputFile("https://telegra.ph/file/f89b0997cb09eda64bddd.png")
    await message.answer_photo(
        image_from_url,
        caption=
        _("<b>Мой Аккаунт:</b>\n"
          "<b>Фамилия:</b> {surname}\n"
          "<b>Имя:</b> {name}\n"
          "<b>Email:</b> {email}\n"
          "<b>Телефон:</b> {phone}\n"
          "👥 <b>Контакты агента</b> \n"
          "Фамилия: {agent_surname}\n"
          "Имя: {agent_name}\n"
          "Email: {agent_email}\n"
          "Телефон: {agent_phone}\n"
          ).format(
            surname=resp['last_name'],
            name=resp['first_name'],
            email=resp['email'],
            phone=resp['phone'],
            agent_surname=resp['agent_contacts']['last_name'],
            agent_name=resp['agent_contacts']['first_name'],
            agent_email=resp['agent_contacts']['email'],
            agent_phone=resp['agent_contacts']['phone'],
        ),
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "my_announcements")
async def my_announcements(callback: types.CallbackQuery, state: FSMContext):
    client = UserAPIClient(user_id=callback.message.chat.id)
    resp = await client.get_my_announcements()
    if resp is None:
        await callback.message.answer(text=_('Ваши данные устарели, нужно перезайти'))
        await logout_handler(message=callback.message, state=state)
        return

    for item in resp:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text=_("Получить геопозицию"),
            callback_data=CoordinateCallbackFactory(longtitude=float(item['map_lon']),
                                                    latitude=float(item['map_lat'])).pack()
        ))
        builder.add(types.InlineKeyboardButton(
            text=_("Просмотреть галерею"),
            callback_data=GalleryCallbackFactory(id=item['id']).pack()
        ))

        await callback.message.answer_photo(
            URLInputFile(client.url + item['main_photo']),
            caption=
            _("<b>Адрес:</b> {address}\n"
              "<b>Актуально:</b> {actual}\n"
              "<b>Модерация:</b> {moderation}\n"
              "<b>Статус модерации:</b> {moderation_status}\n"
              "<b>Документ основания:</b> {grounds_doc}\n"
              "<b>Назначение:</b> {appointment}\n"
              "<b>Количество комнат:</b> {room_count}\n"
              "<b>Планировка:</b> {layout}\n"
              "<b>Жилое состояние:</b> {living_condition}\n"
              "<b>Общая площадь:</b> {square}\n"
              "<b>Площадь кухни:</b> {kitchen_square}\n"
              "<b>Балкон/лоджия:</b> {balcony_or_loggia}\n"
              "<b>Тип отопления:</b> {heating_type}\n"
              "<b>Варианты расчета:</b> {payment_type}\n"
              "<b>Коммисия агенту:</b> {agent_commission}\n"
              "<b>Способ связи:</b> {communication_type}\n"
              "<b>Описание:</b> {description}\n"
              "<b>Цена:</b> {price}\n"
              ).format(
                address=item['address'],
                actual='ДА' if item['is_actual'] else 'НЕТ',
                moderation='Пройдена' if item['is_moderated'] else 'Не пройдена',
                moderation_status=item['moderation_status'] if item['moderation_status'] else '...',
                grounds_doc=item['grounds_doc'],
                appointment=item['appointment'],
                room_count=item['room_count'],
                layout=item['layout'],
                living_condition=item['living_condition'],
                square=item['square'],
                kitchen_square=item['kitchen_square'],
                balcony_or_loggia='ДА' if item['balcony_or_loggia'] else 'НЕТ',
                heating_type=item['heating_type'],
                payment_type=item['payment_type'],
                agent_commission=item['agent_commission'],
                communication_type=item['communication_type'],
                description=item['description'],
                price=item['price'],
            ),
            parse_mode="HTML",
            reply_markup=builder.as_markup()

        )


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
async def show_gallery(callback: types.CallbackQuery, callback_data: CoordinateCallbackFactory, state: FSMContext):
    client = UserAPIClient(user_id=callback.message.chat.id)
    resp = await client.get_gallery_for_announcements(callback_data.id)
    if resp is None:
        await callback.message.answer(text=_('Ваши данные устарели, нужно перезайти'))
        await logout_handler(message=callback.message, state=state)
        return
    gallery = []
    for item in resp['images']:
        gallery.append(URLInputFile(
            item['image']
        ))
    media = [types.InputMediaPhoto(media=photo) for photo in gallery]
    await callback.bot.send_media_group(chat_id=callback.message.chat.id, media=media)
    await callback.answer(
        text="",
    )
