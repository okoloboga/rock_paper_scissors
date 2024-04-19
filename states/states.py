from aiogram.fsm.state import State, StatesGroup


# States
class FSMMain(StatesGroup):

    make_bet = State()
    wait_game = State()
    select_enemy = State()
    in_game = State()
    jettons_import = State()
    jettons_export = State()
    confirm_import = State()
    confirm_export = State()
    new_address = State()
    new_mnemonics = State()
    enter_code = State()
