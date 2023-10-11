from typing import Callable, Dict, Any, Awaitable, Union
from aiogram.utils.i18n import gettext as _

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import TelegramObject, Message, CallbackQuery
from settings import USERS


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            user = USERS.find_one({'user_tg_id': f'{event.chat.id}'})
        else:
            user = USERS.find_one({'user_tg_id': f'{event.from_user.id}'})
        if user and user['is_authenticated']:
            result = await handler(event, data)
            return result

        await event.answer(text=_('Вы не авторизованы'))
