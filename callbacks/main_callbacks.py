from aiogram.filters.callback_data import CallbackData
from typing import Optional


class CoordinateCallbackFactory(CallbackData, prefix=''):
    longtitude: Optional[float] = 0.00
    latitude: Optional[float] = 0.00


class GalleryCallbackFactory(CallbackData, prefix=''):
    id: Optional[int] = None
