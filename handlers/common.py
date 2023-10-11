from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

import keyboards.main as main
from middlewares.auth import AuthMiddleware

router = Router()
router.message.middleware(AuthMiddleware())


@router.message(Command(commands=["cancel"]))
@router.message(F.text == __("Отмена"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer(
        text=_("Действие отменено, вы вернулись в главное меню"),
        reply_markup=main.get_main_kb()
    )
