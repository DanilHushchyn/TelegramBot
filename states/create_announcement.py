from aiogram.fsm.state import StatesGroup, State


class CreateAnnouncement(StatesGroup):
    geolocation = State()
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
    gallery = State()
    complete = State()

