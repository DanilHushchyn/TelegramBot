import base64

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import swipe_api.requests as swipe_api
from handlers import main_menu
from handlers.common import cmd_cancel
from keyboards.main import get_bc_kb
from middlewares.auth import AuthMiddleware
from states.create_announcement import CreateAnnouncement
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

router = Router()  # [1]
router.message.middleware(AuthMiddleware())

grounds_doc = [
    'Собственность'
    , 'Свидетельство о праве на наследство'
]


appointment = [
    'Дом'
    , 'Квартира'
    , 'Коммерческие помещения'
    , 'Офисное помещение'
]


layout = [
    "Студия, санузел"
    , "Классическая"
    , "Европланировка"
    , "Свободная"
]

living_condition = [
    "Черновая"
    , "Ремонт от застройщика"
    , "В жилом состоянии"
]

heating_type = [
    "Центральное"
    , "Автономное"
    , "Альтернативное"
]

balcony_or_loggia = [
    "Да"
    , "Нет"
]

room_count = [
    "1 комнатная"
    , "2 комнатная"
    , "3 комнатная"
    , "4 комнатная"
    , "5 комнатная"
    , "6 комнатная"
    , "7 комнатная"
]
room_count_values = {
    "1 комнатная": 1
    , "2 комнатная": 2
    , "3 комнатная": 3
    , "4 комнатная": 4
    , "5 комнатная": 5
    , "6 комнатная": 6
    , "7 комнатная": 7
}
agent_commission = [
    "5 000 ₴"
    , "15 000 ₴"
    , "30 000 ₴"
]
agent_commission_values = {
    "5 000 ₴": 5000,
    "15 000 ₴": 15000,
    "30 000 ₴": 30000
}
communication_type = [
    "Звонок + сообщение"
    , "Звонок"
    , "Сообщение"
]

payment_type = [
    "Ипотека"
    , "Мат.капитал"
    , "Другое"
]


def make_row_keyboard(items: list[str] = []) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """

    kb = ReplyKeyboardBuilder()

    for item in items:
        kb.button(text=item)

    kb.adjust(3, )
    kb.row(
        types.KeyboardButton(text=_("Назад")),
        types.KeyboardButton(text=_("Отмена"))
    )
    return kb.as_markup(resize_keyboard=True)


@router.message(F.text == __('➕ Создать объявление'))
async def geolocation(message: Message, state: FSMContext):
    await state.set_state(CreateAnnouncement.geolocation)
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text=_("Поделить геолокацией"), request_location=True),
    )
    builder.add(types.KeyboardButton(text=_("Отмена")))
    await message.answer(
        _("Требуется запросить геолокацию для вашего объявления:"),
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@router.message(F.location.as_("location"))
@router.message(CreateAnnouncement.description, F.text == __("Назад"))
async def geolocation_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.geolocation:
        latitude = message.location.latitude
        longitude = message.location.longitude
        await state.update_data(geolocation=[latitude, longitude])
    kb = ReplyKeyboardBuilder()
    kb.row(
        types.KeyboardButton(text=_("Отмена"))
    )
    await message.answer(
        text=_("Теперь пожалуйста укажите адрес:"),
        reply_markup=kb.as_markup(resize_keyboard=True)

    )
    # Устанавливаем пользователю состояние "выбирает address"
    await state.set_state(CreateAnnouncement.address)


@router.message(CreateAnnouncement.grounds_doc, F.text == __("Назад"))
@router.message(CreateAnnouncement.address)
async def address_written(message: Message, state: FSMContext):
    if message.text == _("Отмена"):
        await cmd_cancel(message, state)
        return

    current_state = await state.get_state()
    if current_state == CreateAnnouncement.address:
        await state.update_data(address=message.text)
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите описание:"), allow_sending_without_reply=True,
        reply_markup=make_row_keyboard()
    )
    await state.set_state(CreateAnnouncement.description)


@router.message(CreateAnnouncement.appointment, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.description,
)
async def description_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.description:
        await state.update_data(description=message.text)
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите  документ основания:"),
        reply_markup=make_row_keyboard(grounds_doc)
    )
    await state.set_state(CreateAnnouncement.grounds_doc)


@router.message(CreateAnnouncement.room_count, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.grounds_doc,
    F.text.in_(grounds_doc))
async def grounds_doc_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.grounds_doc:
        await state.update_data(grounds_doc=message.text)
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите  цель:"),
        reply_markup=make_row_keyboard(appointment)
    )
    await state.set_state(CreateAnnouncement.appointment)


@router.message(CreateAnnouncement.layout, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.appointment,
    F.text.in_(appointment))
async def appointment_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.appointment:
        await state.update_data(appointment=message.text)
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите  кол-во комнат:"),
        reply_markup=make_row_keyboard(room_count)
    )
    await state.set_state(CreateAnnouncement.room_count)


@router.message(CreateAnnouncement.living_condition, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.room_count,
    F.text.in_(room_count))
async def room_count_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.room_count:
        await state.update_data(room_count=room_count_values[message.text])

    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите планировку:"),
        reply_markup=make_row_keyboard(layout)
    )
    await state.set_state(CreateAnnouncement.layout)


@router.message(CreateAnnouncement.square, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.layout,
    F.text.in_(layout))
async def layout_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.layout:
        await state.update_data(layout=message.text)

    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите жилое состояние:"),
        reply_markup=make_row_keyboard(living_condition)
    )
    await state.set_state(CreateAnnouncement.living_condition)


@router.message(CreateAnnouncement.kitchen_square, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.living_condition,
    F.text.in_(living_condition))
async def living_condition_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.living_condition:
        await state.update_data(living_condition=message.text)
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите общую площадь:"),
        reply_markup=get_bc_kb()
    )
    await state.set_state(CreateAnnouncement.square)


@router.message(CreateAnnouncement.balcony_or_loggia, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.square,
    F.text.isdecimal()
)
async def square_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.square:
        await state.update_data(square=int(message.text))

    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите площадь кухни:"),
        reply_markup=get_bc_kb(),
    )
    await state.set_state(CreateAnnouncement.kitchen_square)


@router.message(CreateAnnouncement.heating_type, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.kitchen_square,
    F.text.isdecimal()
)
async def kitchen_square_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.kitchen_square:
        data = await state.get_data()
        if data['square'] < int(message.text):
            await message.answer(
                _('Не может общая площадь быть меньше  площади кухни!!! Введите пожалуйста другое значение'))
            return
        await state.update_data(kitchen_square=int(message.text))

    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите есть ли балкон/лоджия:"),
        reply_markup=make_row_keyboard(balcony_or_loggia)
    )
    await state.set_state(CreateAnnouncement.balcony_or_loggia)


@router.message(CreateAnnouncement.payment_type, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.balcony_or_loggia,
    F.text.in_(balcony_or_loggia))
async def balcony_or_loggia_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.balcony_or_loggia:
        if message.text == _('Да'):
            await state.update_data(balcony_or_loggia=True)
        else:
            await state.update_data(balcony_or_loggia=False)
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите тип отопления:"),
        reply_markup=make_row_keyboard(heating_type)
    )
    await state.set_state(CreateAnnouncement.heating_type)


@router.message(CreateAnnouncement.agent_commission, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.heating_type,
    F.text.in_(heating_type))
async def heating_type_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.heating_type:
        await state.update_data(heating_type=message.text)
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите способ оплаты:"),
        reply_markup=make_row_keyboard(payment_type)
    )
    await state.set_state(CreateAnnouncement.payment_type)


@router.message(CreateAnnouncement.communication_type, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.payment_type,
    F.text.in_(payment_type))
async def payment_type_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.payment_type:
        await state.update_data(payment_type=message.text)
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите величину комиссии агента:"),
        reply_markup=make_row_keyboard(agent_commission)
    )
    await state.set_state(CreateAnnouncement.agent_commission)


@router.message(CreateAnnouncement.price, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.agent_commission,
    F.text.in_(agent_commission))
async def agent_commission_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.agent_commission:
        await state.update_data(agent_commission=agent_commission_values[message.text])
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите способ связи:"),
        reply_markup=make_row_keyboard(communication_type)
    )
    await state.set_state(CreateAnnouncement.communication_type)


@router.message(CreateAnnouncement.main_photo, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.communication_type,
    F.text.in_(communication_type)
)
async def communication_type_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.communication_type:
        await state.update_data(communication_type=message.text)
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, укажите цену:"),
        reply_markup=ReplyKeyboardRemove()

    )
    await state.set_state(CreateAnnouncement.price)


@router.message(CreateAnnouncement.gallery, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.price,
    F.text.isdecimal()
)
async def price_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.price:
        await state.update_data(price=int(message.text))
    await message.answer(
        text=_("Спасибо. Теперь, пожалуйста, загрузите главную картинку объявления:"),
    )
    await state.set_state(CreateAnnouncement.main_photo)


@router.message(CreateAnnouncement.complete, F.text == __("Назад"))
@router.message(
    CreateAnnouncement.main_photo,
    F.photo
)
async def main_photo_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.main_photo:
        photo = message.photo[-1]
        await state.update_data(main_photo=photo.file_id)

    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Продолжить"))
    kb.row(
        KeyboardButton(text=_("Назад")),
        KeyboardButton(text=_("Отмена")),
    )
    await message.answer(
        text=_("<b>ВАЖНО:</b>\nТеперь, пожалуйста, загрузите несколько картинок для галереи.\n"
               "При этом по одной картинке в чат для будущей галереи, а не все за раз.\n"
               "После нажмите Продолжить"),
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    await state.set_state(CreateAnnouncement.gallery)
    await state.update_data(gallery=[])


@router.message(
    CreateAnnouncement.gallery,
    F.photo
)
async def gallery_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.gallery:
        data = await state.get_data()
        data['gallery'].append(message.photo[-1].file_id)
        await state.update_data(gallery=data['gallery'])


@router.message(
    CreateAnnouncement.gallery,
    F.text == __('Продолжить')
)
async def checked_gallery(message: Message, state: FSMContext):
    await state.set_state(CreateAnnouncement.complete)
    data = await state.get_data()
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("➕ Создать"))
    kb.row(
        KeyboardButton(text=_("Назад")),
        KeyboardButton(text=_("Отмена")),
    )
    await message.answer_photo(
        data['main_photo'],
        caption=
        _("<b>Адрес:</b> {address}\n"
          "<b>Описание:</b> {description}\n"
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
          "<b>Цена:</b> {price}\n"
          "<b>Всё верно?</b>\n"
          ).format(
            address=data['address'],
            description=data['description'],
            grounds_doc=data['grounds_doc'],
            appointment=data['appointment'],
            room_count=data['room_count'],
            layout=data['layout'],
            living_condition=data['living_condition'],
            square=data['square'],
            kitchen_square=data['kitchen_square'],
            balcony_or_loggia='ДА' if data['balcony_or_loggia'] else 'НЕТ',
            heating_type=data['heating_type'],
            payment_type=data['payment_type'],
            agent_commission=data['agent_commission'],
            communication_type=data['communication_type'],
            price=data['price'],
        ),
        parse_mode="HTML",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )
    if not data['gallery']:
        await message.answer(text=_('<b>Ваша галерея пуста но всё ок</b>'), parse_mode="HTML")
    else:
        await message.answer(text=_('<b>Ваша галерея:</b>'), parse_mode="HTML")
        media = [types.InputMediaPhoto(media=photo) for photo in data['gallery']]
        await message.bot.send_media_group(chat_id=message.chat.id, media=media)


@router.message(
    CreateAnnouncement.complete,
    F.text == __('➕ Создать')
)
async def announcement_complete(message: Message, state: FSMContext):
    data = await state.get_data()
    file = await message.bot.get_file(data['main_photo'])
    result = await message.bot.download_file(file.file_path)
    main_photo64 = base64.b64encode(result.read()).decode('ascii')
    gallery64 = []
    for key, value in enumerate(data['gallery']):
        file = await message.bot.get_file(value)
        result = await message.bot.download_file(file.file_path)
        photo64 = base64.b64encode(result.read())
        gallery64.append(
            {
                "order": key + 1,
                "image": photo64.decode('ascii')
            }
        )

    client = swipe_api.UserAPIClient(user_id=message.chat.id)

    resp = await client.create_announcement(data=data, main_photo64=main_photo64, gallery64=gallery64)
    if resp is None:
        await message.answer(text=_('Ваши данные устарели, нужно перезайти'))
        await main_menu.logout_handler(message=message, state=state)
        return
    await message.answer(text=_('<b>Ваше объявление успешно создано</b>'), parse_mode="HTML")
    await state.clear()
    await main_menu.cmd_start(message=message)
