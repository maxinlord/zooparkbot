from aiogram.fsm.state import StatesGroup, State


class User(StatesGroup):
    main = State()

class Admin(StatesGroup):
    main = State()
    get_discount = State()
    get_days_sub = State()
    get_num_enable_triggers = State()