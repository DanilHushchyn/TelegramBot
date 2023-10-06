# from aiogram import Router, types, F
import pymongo
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import KeyboardBuilder, ReplyKeyboardBuilder

from handlers.main_menu import cmd_start
from keyboards.authorization import get_language_kb, get_authorization_kb, get_register_keyboard, get_back_register
from settings import USERS
from states.authorization import Start, Login, Register
from validators import validate_email, validate_password
import httpx

router = Router()


# region Start Bot
@router.message(Command(commands=["start"]))
@router.message(Start.login_or_register, F.text.casefold() == 'выбор языка')
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Start.language)
    await message.answer(
        'Выберите язык...',
        reply_markup=get_language_kb()
    )


@router.message(Start.language, F.text.casefold() == 'english')
@router.message(Start.language, F.text.casefold() == 'русский')
@router.message(Login.complete, F.text.casefold() == 'отмена')
@router.message(Login.password, F.text.casefold() == 'отмена')
@router.message(Login.email, F.text.casefold() == 'отмена')
@router.message(Register.first_name, F.text.casefold() == 'отмена')
@router.message(Register.last_name, F.text.casefold() == 'отмена')
@router.message(Register.email, F.text.casefold() == 'отмена')
@router.message(Register.password, F.text.casefold() == 'отмена')
@router.message(Register.complete, F.text.casefold() == 'отмена')
async def authorization_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Start.login_or_register)
    await message.answer(
        'Выберите...',
        reply_markup=get_authorization_kb()
    )


@router.message(Login.password, F.text.casefold() == 'назад')
@router.message(Start.login_or_register, F.text.casefold() == 'вход')
async def login_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Login.email)
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    await message.answer(
        'Введите свой email пожалуйста',
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Login.email)
async def login_email_handler(message: Message, state: FSMContext) -> None:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    kb.adjust(2)
    email = message.text
    if validate_email(email) is False:
        await message.answer(
            'Неверный формат email, попробуйте ещё раз',
            reply_markup=kb.as_markup(resize_keyboard=True)
        )
        return
    else:
        await state.update_data(email=email)

    await state.set_state(Login.password)
    await message.answer(
        'Введите свой пароль пожалуйста',
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Login.password)
async def login_password_handler(message: Message, state: FSMContext) -> None:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Назад')
    kb.button(text='Отмена')
    kb.adjust(2)
    if validate_password(password=message.text):
        await state.update_data(password=message.text)
    else:
        await message.answer(text='Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов',
                             reply_markup=kb.as_markup(resize_keyboard=True))
        return

    await state.set_state(Login.complete)

    data = await state.get_data()
    text = (
        'Проверьте данные:\n\n'
        'Email: {email}\n'
        'Пароль: {password}\n'
        'Всё верно?'
    ).format(email=data["email"], password=data["password"])
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Войти'),
            ],
            [
                KeyboardButton(text='Отмена')
            ]
        ],
        resize_keyboard=True
    )
    await message.answer(
        text=text,
        reply_markup=keyboard
    )


@router.message(Login.complete, F.text.casefold() == 'войти')
async def login_complete_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    async with httpx.AsyncClient(http2=True) as client:
        resp: httpx.Response = await client.post('http://127.0.0.0:8000/api/v1/auth/login/', data=data)

    if resp.status_code == 200:
        data = {
            'user_api_id': f'{resp.json()["user"]["pk"]}',
            'access': f'{resp.json()["access"]}',
            'user_tg_id': f'{message.chat.id}',
            'email': f'{resp.json()["user"]["email"]}',
            'first_name': f'{resp.json()["user"]["first_name"]}',
            'last_name': f'{resp.json()["user"]["last_name"]}',
            'is_authenticated': True,
        }
        USERS.update_one(filter={'user_tg_id': str(message.chat.id)}, update={"$set": data}, upsert=True)
        await client.aclose()
        await cmd_start(message)



@router.message(Register.last_name, F.text.casefold() == 'назад')
@router.message(Start.login_or_register, F.text.casefold() == 'регистрация')
async def register_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Register.first_name)
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    await message.answer(
        'Введите своё имя пожалуйста',
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Register.complete, F.text.casefold() == 'редактировать имя')
async def register_edit_first_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Измените имя если нужно",
        reply_markup=get_back_register()
    )
    await state.set_state(Register.edit_first_name)


@router.message(Register.edit_first_name)
async def register_edit_first_name_check(message: Message, state: FSMContext) -> None:
    if message.text.casefold() == 'вернутся к регистрации':
        await register_complete_handler(message, state)
    else:
        first_name = message.text.lower()
        await state.update_data(first_name=first_name)
        await register_complete_handler(message, state)


@router.message(Register.email, F.text.casefold() == 'назад')
@router.message(Register.first_name)
async def register_first_name_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == Register.first_name:
        await state.update_data(first_name=message.text)
    await state.set_state(Register.last_name)
    kb = ReplyKeyboardBuilder()
    kb.button(text='Назад')
    kb.button(text='Отмена')
    await message.answer(
        'Введите свою фамилию пожалуйста',
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Register.complete, F.text.casefold() == 'редактировать фамилию')
async def register_edit_last_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Измените фамилию если нужно",
        reply_markup=get_back_register()
    )
    await state.set_state(Register.edit_last_name)


@router.message(Register.edit_last_name)
async def register_last_name_check(message: Message, state: FSMContext) -> None:
    if message.text.casefold() == 'вернутся к регистрации':
        await register_complete_handler(message, state)
    else:
        last_name = message.text.casefold()
        await state.update_data(last_name=last_name)
        await register_complete_handler(message, state)


@router.message(Register.password, F.text.casefold() == 'назад')
@router.message(Register.last_name)
async def register_last_name_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == Register.last_name:
        await state.update_data(last_name=message.text)
    await state.set_state(Register.email)
    kb = ReplyKeyboardBuilder()
    kb.button(text='Назад')
    kb.button(text='Отмена')
    await message.answer(
        'Введите свой email пожалуйста',
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Register.complete, F.text.casefold() == 'редактировать email')
async def register_edit_email_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Измените email если нужно",
        reply_markup=get_back_register()
    )
    await state.set_state(Register.edit_email)


@router.message(Register.edit_email)
async def register_edit_email_check(message: Message, state: FSMContext) -> None:
    if message.text.casefold() == 'вернутся к регистрации':
        await register_complete_handler(message, state)
    else:
        email = message.text
        if validate_email(email) is False:
            await message.answer(
                'Неверный формат email, попробуйте ещё раз',
                reply_markup=get_back_register()
            )
        else:
            await state.update_data(email=email)
            await register_complete_handler(message, state)


@router.message(Register.email)
async def register_email_handler(message: Message, state: FSMContext) -> None:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Назад')
    kb.button(text='Отмена')
    if validate_email(email=message.text) is False:
        await message.answer(
            'Неверный формат email, попробуйте ещё раз',
            reply_markup=kb.as_markup(resize_keyboard=True)
        )
        return
    await state.update_data(email=message.text)
    await state.set_state(Register.password)
    await message.answer(
        'Введите свой пароль пожалуйста',
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Register.complete, F.text.casefold() == 'редактировать пароль')
async def register_edit_password_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Измените пароль если нужно",
        reply_markup=get_back_register()
    )
    await state.set_state(Register.edit_password)


@router.message(Register.edit_password)
async def register_edit_password_check(message: Message, state: FSMContext) -> None:
    if message.text.casefold() == 'вернутся к регистрации':
        await register_complete_handler(message, state)
    else:
        if validate_password(password=message.text):
            await state.update_data(password=message.text)
        else:
            await message.answer(text='Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов')
            return
        await register_complete_handler(message, state)


@router.message(F.text.casefold() == 'Вернутся к регистрации')
@router.message(Register.password)
async def register_complete_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    kb = ReplyKeyboardBuilder()
    kb.button(text='Назад')
    kb.button(text='Отмена')
    if current_state == Register.password:
        if validate_password(password=message.text):
            await state.update_data(password=message.text)
        else:
            await message.answer(text='Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов',
                                 reply_markup=kb.as_markup(resize_keyboard=True))
            return

    await state.set_state(Register.complete)
    data = await state.get_data()
    text = (
        'Проверьте данные:\n\n'
        'Имя: {first_name}\n'
        'Фамилия: {last_name}\n'
        'Email: {email}\n'
        'Пароль: {password}\n'
        'Всё верно?'
    ).format(first_name=data['first_name'], last_name=data['last_name'], email=data["email"], password=data["password"])
    await message.answer(
        text=text,
        reply_markup=get_register_keyboard()
    )

# @router.message(Register.complete)
# async def register_complete_handler(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     text = (
#         'Проверьте данные:\n\n'
#         'Имя: {first_name}\n'
#         'Фамилия: {last_name}\n'
#         'Email: {email}\n'
#         'Пароль: {password}\n'
#         'Всё верно?'
#     ).format(first_name=data['first_name'], last_name=data['last_name'], email=data["email"], password=data["password"])
#     keyboard = ReplyKeyboardMarkup(
#         keyboard=[
#             [
#                 KeyboardButton(text='Войти'),
#             ],
#             [
#                 KeyboardButton(text='Отмена')
#             ]
#         ],
#         resize_keyboard=True
#     )
#     await message.answer(
#         text=text,
#         reply_markup=keyboard
#     )
