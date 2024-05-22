from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    main = State()
    start_reg = State()
    enter_custom_quantity_animals = State()

class AdminState(StatesGroup):
    main = State()
    