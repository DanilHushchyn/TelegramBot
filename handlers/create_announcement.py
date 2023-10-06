import base64
import json
import urllib

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from handlers.common import cmd_cancel

router = Router()  # [1]

grounds_doc = [
    'Собственность', 'Свидетельство о праве на наследство'
]
appointment = [
    'Дом', 'Квартира', 'Коммерческие помещения', 'Офисное помещение',
]
layout = [
    "Студия, санузел"
    , "Классическая"
    , "Европланировка"
    , "Свободная"
]
living_condition = [
"Черновая"
    ,"Ремонт от застройщика"
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
agent_commission = [
    "5 000 ₴"
    , "15 000 ₴"
    , "30 000 ₴"
]
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


class CreateAnnouncement(StatesGroup):
    address = State()
    description = State()
    grounds_doc = State()
    appointment = State()
    room_count = State()
    layout = State()
    living_condition = State()
    kitchen_square = State()
    balcony_or_loggia = State()
    heating_type = State()
    payment_type = State()
    agent_commission = State()
    communication_type = State()
    square = State()
    price = State()
    main_photo = State()


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
        types.KeyboardButton(text="Назад"),
        types.KeyboardButton(text="Отмена")
    )
    return kb.as_markup(resize_keyboard=True)


@router.message(CreateAnnouncement.description, F.text.casefold() == 'назад')
@router.message(F.text == '➕ Создать объявление')
async def create_announcement(message: Message, state: FSMContext):
    kb = ReplyKeyboardBuilder()
    kb.row(
        types.KeyboardButton(text="Отмена")
    )
    await message.answer(
        text="Укажите адрес:",
        reply_markup=kb.as_markup(resize_keyboard=True)

    )
    # Устанавливаем пользователю состояние "выбирает address"
    await state.set_state(CreateAnnouncement.address)


@router.message(CreateAnnouncement.grounds_doc, F.text.casefold() == 'назад')
@router.message(CreateAnnouncement.address, )
async def address_written(message: Message, state: FSMContext):
    if message.text.casefold() == 'отмена':
        await cmd_cancel(message, state)
        return

    current_state = await state.get_state()
    if current_state == CreateAnnouncement.address:
        await state.update_data(address=message.text)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите описание:",

    )
    await state.set_state(CreateAnnouncement.description)


@router.message(CreateAnnouncement.appointment, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.description,
)
async def description_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.description:
        await state.update_data(description=message.text)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите  документ основания:",
        reply_markup=make_row_keyboard(grounds_doc)
    )
    await state.set_state(CreateAnnouncement.grounds_doc)


@router.message(CreateAnnouncement.room_count, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.grounds_doc,
    F.text.in_(grounds_doc))
async def grounds_doc_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.grounds_doc:
        await state.update_data(grounds_doc=message.text)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите  цель:",
        reply_markup=make_row_keyboard(appointment)
    )
    await state.set_state(CreateAnnouncement.appointment)


@router.message(CreateAnnouncement.layout, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.appointment,
    F.text.in_(appointment))
async def appointment_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.appointment:
        await state.update_data(appointment=message.text)

    data = await state.get_data()
    await message.answer(f"Collected Data: {data}")

    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите  кол-во комнат:",
        reply_markup=make_row_keyboard(room_count)
    )
    await state.set_state(CreateAnnouncement.room_count)


@router.message(CreateAnnouncement.living_condition, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.room_count,
    F.text.in_(room_count))
async def room_count_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.room_count:
        await state.update_data(room_count=message.text)

    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите планировку:",
        reply_markup=make_row_keyboard(layout)
    )
    await state.set_state(CreateAnnouncement.layout)


@router.message(CreateAnnouncement.square, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.layout,
    F.text.in_(layout))
async def layout_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.layout:
        await state.update_data(layout=message.text)

    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите жилое состояние:",
        reply_markup=make_row_keyboard(living_condition)
    )
    await state.set_state(CreateAnnouncement.living_condition)


@router.message(CreateAnnouncement.kitchen_square, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.living_condition,
    F.text.in_(living_condition))
async def living_condition_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.address:
        await state.update_data(living_condition=message.text)

    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите общую площадь:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CreateAnnouncement.square)


@router.message(CreateAnnouncement.balcony_or_loggia, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.square,
    F.text.isdecimal()
)
async def square_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.square:
        await state.update_data(square=int(message.text))

    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите площадь кухни:",
    )
    await state.set_state(CreateAnnouncement.kitchen_square)


@router.message(CreateAnnouncement.heating_type, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.kitchen_square,
    F.text.isdecimal()
)
async def kitchen_square_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.kitchen_square:
        data = await state.get_data()
        if data['square'] < int(message.text):
            await message.answer('Не может общая площадь быть меньше  площади кухни!!! Введите пожалуйста другое значение')
            return
        await state.update_data(kitchen_square=int(message.text))

    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите есть ли балкон/лоджия:",
        reply_markup=make_row_keyboard(balcony_or_loggia)
    )
    await state.set_state(CreateAnnouncement.balcony_or_loggia)


@router.message(CreateAnnouncement.payment_type, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.balcony_or_loggia,
    F.text.in_(balcony_or_loggia))
async def balcony_or_loggia_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.balcony_or_loggia:
        if message.text == 'Да':
            await state.update_data(balcony_or_loggia=True)
        else:
            await state.update_data(balcony_or_loggia=False)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите тип отопления:",
        reply_markup=make_row_keyboard(heating_type)
    )
    await state.set_state(CreateAnnouncement.heating_type)


@router.message(CreateAnnouncement.agent_commission, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.heating_type,
    F.text.in_(heating_type))
async def heating_type_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.heating_type:
        await state.update_data(heating_type=message.text)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите способ оплаты:",
        reply_markup=make_row_keyboard(payment_type)
    )
    await state.set_state(CreateAnnouncement.payment_type)


@router.message(CreateAnnouncement.communication_type, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.payment_type,
    F.text.in_(payment_type))
async def payment_type_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.payment_type:
        await state.update_data(payment_type=message.text)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите величину комиссии агента:",
        reply_markup=make_row_keyboard(agent_commission)
    )
    await state.set_state(CreateAnnouncement.agent_commission)


@router.message(CreateAnnouncement.price, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.agent_commission,
    F.text.in_(agent_commission))
async def agent_commission_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.agent_commission:
        await state.update_data(agent_commission=message.text)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите способ связи:",
        reply_markup=make_row_keyboard(communication_type)
    )
    await state.set_state(CreateAnnouncement.communication_type)


@router.message(CreateAnnouncement.main_photo, F.text.casefold() == 'назад')
@router.message(
    CreateAnnouncement.communication_type,
    F.text.in_(communication_type)
)
async def communication_type_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.communication_type:
        await state.update_data(communication_type=message.text)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, укажите цену:",
        reply_markup=ReplyKeyboardRemove()

    )
    await state.set_state(CreateAnnouncement.price)


@router.message(
    CreateAnnouncement.price,
    F.text.isdecimal()
)
async def price_written(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.price:
        await state.update_data(price=int(message.text))
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, загрузите главную картинку объявления:",
    )
    await state.set_state(CreateAnnouncement.main_photo)


@router.message(
    CreateAnnouncement.main_photo,

    F.photo
)
async def main_photo_written(message: Message, state: FSMContext):
    photo = message.photo[-1]
    current_state = await state.get_state()
    if current_state == CreateAnnouncement.main_photo:
        await state.update_data(main_photo=photo.file_id)

    data = await state.get_data()
    await message.answer(f"Collected Data: {data}")
