from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks.main_callbacks import CoordinateCallbackFactory, GalleryCallbackFactory
import handlers.main_menu as main_menu
from middlewares.auth import AuthMiddleware
import swipe_api.requests as swipe_api
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

router = Router()  # [1]
router.message.middleware(AuthMiddleware())


@router.message(F.text == __('🗂 Список объявлений'))
async def all_announcements(message: Message, state: FSMContext, page_num=0):
    client = swipe_api.UserAPIClient(user_id=message.chat.id)
    resp = await client.get_all_announcements()
    if resp is None:
        await message.answer(text=_('Ваши данные устарели, нужно перезайти'))
        await main_menu.logout_handler(message=message, state=state)
        return
    if page_num + 1 > len(resp):
        page_num = 0
    elif page_num + 1 <= 0:
        page_num = len(resp) - 1
    item = resp[page_num]

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="←",
        callback_data=f"previous_{page_num - 1}")
    )
    builder.add(types.InlineKeyboardButton(
        text=f"{page_num + 1}/{len(resp)}",
        callback_data="page_button")
    )
    builder.add(types.InlineKeyboardButton(
        text="→",
        callback_data=f"next_{page_num + 1}")
    )

    builder.row(types.InlineKeyboardButton(
        text=_("Получить геопозицию"),
        callback_data=CoordinateCallbackFactory(longtitude=float(item['map_lon']),
                                                latitude=float(item['map_lat'])).pack()
    ),
        types.InlineKeyboardButton(
            text=_("Просмотреть галерею"),
            callback_data=GalleryCallbackFactory(id=item['id']).pack()
        )
    )

    await message.answer_photo(
        URLInputFile(item['main_photo']),
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
        reply_markup=builder.as_markup(resize_keyboard=True)

    )


@router.callback_query(F.data.startswith("next_"))
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    number = callback.data.split('_')[1]
    await all_announcements(callback.message, state, int(number))
    await callback.answer()


@router.callback_query(F.data.startswith("previous_"))
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    number = callback.data.split('_')[1]
    await all_announcements(callback.message, state, int(number))
    await callback.answer()
