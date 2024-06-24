from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    start_reg_step = State()
    main_menu = State()
    zoomarket_menu = State()
    unity_menu = State()
    enter_name_unity_step = State()
    random_merchant_window = State()
    rmerchant_enter_custom_qa_step = State()
    rshop_enter_custom_qa_step = State()
    for_while_shell = State()
    avi_enter_custom_qa_step = State()
    exchange_bank_step = State()
    game = State()
    send_mess_to_support = State()
    answer_on_question = State()

class AdminState(StatesGroup):
    main = State()
    