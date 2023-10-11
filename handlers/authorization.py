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
from swipe_api.requests import UserAPIClient
from validators import validate_email, validate_password
import httpx

router = Router()
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __


# region Start Bot
@router.message(Command(commands=["start"]))
@router.message(Start.login_or_register, F.text == __('Выбор языка'))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Start.language)
    await message.answer(
        _('Выберите язык...'),
        reply_markup=get_language_kb()
    )


@router.message(Start.language, F.text == 'English')
@router.message(Start.language, F.text == 'Русский')
@router.message(Login.complete, F.text == __("Отмена"))
@router.message(Login.password, F.text == __("Отмена"))
@router.message(Login.email, F.text == __("Отмена"))
@router.message(Register.first_name, F.text == __("Отмена"))
@router.message(Register.last_name, F.text == __("Отмена"))
@router.message(Register.email, F.text == __("Отмена"))
@router.message(Register.password, F.text == __("Отмена"))
@router.message(Register.complete, F.text == __("Отмена"))
async def authorization_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Start.login_or_register)
    await message.answer(
        _('Выберите...'),
        reply_markup=get_authorization_kb()
    )


@router.message(Login.password, F.text == __("Назад"))
@router.message(Start.login_or_register, F.text == __('Вход'))
async def login_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Login.email)
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Отмена"))
    await message.answer(
        _('Введите свой email пожалуйста'),
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Login.email)
async def login_email_handler(message: Message, state: FSMContext) -> None:
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Отмена"))
    kb.adjust(2)
    email = message.text
    if validate_email(email) is False:
        await message.answer(
            _('Неверный формат email, попробуйте ещё раз'),
            reply_markup=kb.as_markup(resize_keyboard=True)
        )
        return
    else:
        await state.update_data(email=email)

    await state.set_state(Login.password)
    await message.answer(
        _('Введите свой пароль пожалуйста'),
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Login.password)
async def login_password_handler(message: Message, state: FSMContext) -> None:
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Назад"))
    kb.button(text=_("Отмена"))
    kb.adjust(2)
    if validate_password(password=message.text):
        await state.update_data(password=message.text)
    else:
        await message.answer(text=_('Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов'),
                             reply_markup=kb.as_markup(resize_keyboard=True))
        return

    await state.set_state(Login.complete)

    data = await state.get_data()
    text = _(
        'Проверьте данные:\n\n'
        'Email: {email}\n'
        'Пароль: {password}\n'
        'Всё верно?'
    ).format(email=data["email"], password=data["password"])
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_('Войти')),
            ],
            [
                KeyboardButton(text=_("Отмена"))
            ]
        ],
        resize_keyboard=True
    )
    await message.answer(
        text=text,
        reply_markup=keyboard
    )


@router.message(Login.complete, F.text == __('Войти'))
async def login_complete_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    client = UserAPIClient(user_id=message.chat.id)
    if await client.login(data):
        await cmd_start(message)
    else:
        await message.answer(text=_('Почта или пароль указаны не верно или вы не подтвердили почту'))
        await login_handler(message=message, state=state)


@router.message(Register.last_name, F.text == __("Назад"))
@router.message(Start.login_or_register, F.text == __('Регистрация'))
async def register_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Register.first_name)
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Отмена"))
    await message.answer(
        _('Введите своё имя пожалуйста'),
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Register.complete, F.text == __('Редактировать имя'))
async def register_edit_first_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        _("Измените имя если нужно"),
        reply_markup=get_back_register()
    )
    await state.set_state(Register.edit_first_name)


@router.message(Register.edit_first_name)
async def register_edit_first_name_check(message: Message, state: FSMContext) -> None:
    if message.text == __('вернутся к регистрации'):
        await register_complete_handler(message, state)
    else:
        first_name = message.text.lower()
        await state.update_data(first_name=first_name)
        await register_complete_handler(message, state)


@router.message(Register.email, F.text == __("Назад"))
@router.message(Register.first_name)
async def register_first_name_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == Register.first_name:
        await state.update_data(first_name=message.text)
    await state.set_state(Register.last_name)
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Назад"))
    kb.button(text=_("Отмена"))
    await message.answer(
        _('Введите свою фамилию пожалуйста'),
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Register.complete, F.text == __('Редактировать фамилию'))
async def register_edit_last_name_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        _("Измените фамилию если нужно"),
        reply_markup=get_back_register()
    )
    await state.set_state(Register.edit_last_name)


@router.message(Register.edit_last_name)
async def register_last_name_check(message: Message, state: FSMContext) -> None:
    if message.text == _('Вернутся к регистрации'):
        await register_complete_handler(message, state)
    else:
        last_name = message.text
        await state.update_data(last_name=last_name)
        await register_complete_handler(message, state)


@router.message(Register.password, F.text == __("Назад"))
@router.message(Register.last_name)
async def register_last_name_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == Register.last_name:
        await state.update_data(last_name=message.text)
    await state.set_state(Register.email)
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Назад"))
    kb.button(text=_("Отмена"))
    await message.answer(
        _('Введите свой email пожалуйста'),
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Register.complete, F.text == __('Редактировать email'))
async def register_edit_email_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        _("Измените email если нужно"),
        reply_markup=get_back_register()
    )
    await state.set_state(Register.edit_email)


@router.message(Register.edit_email)
async def register_edit_email_check(message: Message, state: FSMContext) -> None:
    if message.text == _('Вернутся к регистрации'):
        await register_complete_handler(message, state)
    else:
        email = message.text
        if validate_email(email) is False:
            await message.answer(
                _('Неверный формат email, попробуйте ещё раз'),
                reply_markup=get_back_register()
            )
        else:
            await state.update_data(email=email)
            await register_complete_handler(message, state)


@router.message(Register.email)
async def register_email_handler(message: Message, state: FSMContext) -> None:
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Назад"))
    kb.button(text=_("Отмена"))
    if validate_email(email=message.text) is False:
        await message.answer(
            _('Неверный формат email, попробуйте ещё раз'),
            reply_markup=kb.as_markup(resize_keyboard=True)
        )
        return
    await state.update_data(email=message.text)
    await state.set_state(Register.password)
    await message.answer(
        _('Введите свой пароль пожалуйста'),
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(Register.complete, F.text == __('Редактировать пароль'))
async def register_edit_password_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        _("Измените пароль если нужно"),
        reply_markup=get_back_register()
    )
    await state.set_state(Register.edit_password)


@router.message(Register.edit_password)
async def register_edit_password_check(message: Message, state: FSMContext) -> None:
    if message.text == _('Вернутся к регистрации'):
        await register_complete_handler(message, state)
    else:
        if validate_password(password=message.text):
            await state.update_data(password=message.text)
        else:
            await message.answer(text=_('Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов'))
            return
        await register_complete_handler(message, state)


@router.message(F.text == __('Вернутся к регистрации'))
@router.message(Register.password)
async def register_complete_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Назад"))
    kb.button(text=_("Отмена"))
    if current_state == Register.password:
        if validate_password(password=message.text):
            await state.update_data(password=message.text)
        else:
            await message.answer(text=_('Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов'),
                                 reply_markup=kb.as_markup(resize_keyboard=True))
            return

    await state.set_state(Register.complete)
    data = await state.get_data()
    text = _(
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


@router.message(F.text == __('Зарегистрироваться'))
@router.message(Register.complete)
async def register_complete_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    client = UserAPIClient(user_id=message.chat.id)
    if await client.register(data):
        await message.answer(text=_('Письмо с подтверждением выслано вам на почту, подтвердите там регистрацию и можете'
                                  'заходить.'))
    else:
        await message.answer(text=_('Пользователь с таким email уже зарегистрирован'))
    await authorization_handler(message=message, state=state)
