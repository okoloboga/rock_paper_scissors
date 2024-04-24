from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fluentogram import TranslatorRunner


# Main keyboard
def play_account_kb(i18n: TranslatorRunner):
    button_play = InlineKeyboardButton(text=i18n.play(),
                                       callback_data='play')
    button_account = InlineKeyboardButton(text=i18n.account(),
                                          callback_data='account')
    return InlineKeyboardMarkup(inline_keyboard=[[button_play], [button_account]])


# Import, export and refcode
def import_export_kb(i18n: TranslatorRunner):
    button_import = InlineKeyboardButton(text=i18n.tokenimport(),
                                         callback_data='import')
    button_export = InlineKeyboardButton(text=i18n.tokenexport(),
                                         callback_data='export')
    button_get_refcode = InlineKeyboardButton(text=i18n.refcode(),
                                              callback_data='get_refcode')
    button_enter_code = InlineKeyboardButton(text=i18n.enter.code(),
                                             callback_data='enter_code')
    button_back = InlineKeyboardButton(text=i18n.back(),
                                       callback_data='back')
    return InlineKeyboardMarkup(inline_keyboard=[[button_import, button_export],
                                                 [button_enter_code, button_get_refcode], [button_back]])


# Canceling waiting for enemy
def back_kb(i18n: TranslatorRunner):
    button_back = InlineKeyboardButton(text=i18n.back(),
                                       callback_data='back')
    return InlineKeyboardMarkup(inline_keyboard=[[button_back]])


# Confirm game
def create_join_kb(i18n: TranslatorRunner):
    button_create = InlineKeyboardButton(text=i18n.create.button(),
                                         callback_data='create')
    button_join = InlineKeyboardButton(text=i18n.join.button(),
                                       callback_data='join')
    button_back = InlineKeyboardButton(text=i18n.back(),
                                       callback_data='back')
    return InlineKeyboardMarkup(inline_keyboard=[[button_create, button_join], [button_back]])


# Enemy select
def select_enemy(rooms: dict, i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    button_back = InlineKeyboardButton(text=i18n.back(),
                                       callback_data='back')
    buttons_enemy: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=i18n.button.rooms(user_id=key[2:], bet=value),
                             callback_data=(str(key[2:] + ' ' + value))) for key, value in rooms.items()]
    return InlineKeyboardMarkup(inline_keyboard=[buttons_enemy, [button_back]])


# Confirming game with joined enemy
def game_confirm(i18n: TranslatorRunner):
    button_confirm = InlineKeyboardButton(text=i18n.great(),
                                          callback_data='game_confirm')
    return InlineKeyboardMarkup(inline_keyboard=[[button_confirm]])


# Main game keyboard
def game_process_kb(i18n: TranslatorRunner):
    button_1 = InlineKeyboardButton(text=i18n.rock(),
                                    callback_data='rock')
    button_2 = InlineKeyboardButton(text=i18n.scissors(),
                                    callback_data='scissors')
    button_3 = InlineKeyboardButton(text=i18n.paper(),
                                    callback_data='paper')
    button_end_game = InlineKeyboardButton(text=i18n.end.game(),
                                           callback_data='end_game')
    return InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_end_game]])


# Confirm leaved enemy
def enemy_leaved_ok(i18n: TranslatorRunner):
    button_ok = InlineKeyboardButton(text=i18n.great(),
                                     callback_data='back')
    return InlineKeyboardMarkup(inline_keyboard=[[button_ok]])


# Bets keyboard
def bet_kb(i18n: TranslatorRunner):
    button_1 = InlineKeyboardButton(text=i18n.b1(),
                                    callback_data='b1')
    button_2 = InlineKeyboardButton(text=i18n.b2(),
                                    callback_data='b2')
    button_3 = InlineKeyboardButton(text=i18n.b3(),
                                    callback_data='b3')
    button_4 = InlineKeyboardButton(text=i18n.b4(),
                                    callback_data='b4')
    button_5 = InlineKeyboardButton(text=i18n.b5(),
                                    callback_data='b5')
    button_25 = InlineKeyboardButton(text=i18n.b25(),
                                     callback_data='b25')
    button_back = InlineKeyboardButton(text=i18n.back(),
                                       callback_data='back')
    return InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2, button_3, button_4], [button_5, button_25], [button_back]])


# Enter jettons value
def digit_inline(i18n: TranslatorRunner):
    button_back = InlineKeyboardButton(text=i18n.back(),
                                       callback_data='back')
    digit_keyboard = []
    for j in range(3):
        digit_keyboard.append(
            [InlineKeyboardButton(text=str(i + j * 3 + 1), callback_data=str(i + j * 3 + 1)) for i in range(3)])

    digit_keyboard.append([InlineKeyboardButton(text='<', callback_data='<'),
                           InlineKeyboardButton(text='0', callback_data='0'),
                           InlineKeyboardButton(text='ok', callback_data='ok')])
    digit_keyboard.append([button_back])

    return InlineKeyboardMarkup(inline_keyboard=digit_keyboard)
