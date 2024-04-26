from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from redis import asyncio as aioredis
from fluentogram import TranslatorRunner

from keyboards.keyboards import back_kb, import_export_kb, play_account_kb, digit_inline
from database.database import users_db
from states.states import FSMMain
from filters.filters import IsWallet, IsMnemonics, IsImport, IsExport
from services.ton_services import jetton_import, jetton_export, check_balance

router = Router()


# IMPORT button pressing
@router.callback_query(F.data == 'import')
async def process_import_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)
    user = await r.hgetall(str(callback.from_user.id))
    # Create new local wallet
    if user[b'export_address'] == b'0':
        try:
            await callback.message.edit_text(text=i18n.new.wallet(),
                                             reply_markup=back_kb(i18n))
            await state.set_state(FSMMain.new_address)
        except TelegramBadRequest:
            await callback.answer()
    else:
        try:
            await state.update_data(up_down=callback.data)
            await state.update_data(price='')
            await callback.message.edit_text(text=i18n.enter.forimport(price=str((await state.get_data())['price'])),
                                             reply_markup=digit_inline(i18n))
            await state.set_state(FSMMain.jettons_import)
        except TelegramBadRequest:
            await callback.answer()


# EXPORT button pressing
@router.callback_query(F.data == 'export')
async def process_export_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)
    user = await r.hgetall(str(callback.from_user.id))
    # Need to add new wallet
    if user[b'mnemonics'] == b'0':
        try:
            await callback.message.edit_text(text=i18n.new.wallet(),
                                             reply_markup=back_kb(i18n))
            await state.set_state(FSMMain.new_address)
        except TelegramBadRequest:
            await callback.answer()
    else:
        try:
            await state.update_data(up_down=callback.data)
            await state.update_data(price='')
            await callback.message.edit_text(text=i18n.enter.forexport(price=str((await state.get_data())['price'])),
                                             reply_markup=digit_inline(i18n))
            await state.set_state(FSMMain.jettons_export)
        except TelegramBadRequest:
            await callback.answer()


"""ADDING A WALLET"""


# User enter wallet address
@router.message(IsWallet(), StateFilter(FSMMain.new_address))
async def process_address_input(message: Message, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)
    user = await r.hgetall(str(message.from_user.id))
    user[b'export_address'] = message.text
    await r.hmset(str(message.from_user.id), user)
    await message.answer(text=i18n.new.mnemonics(),
                         reply_markup=back_kb(i18n))
    await state.set_state(FSMMain.new_mnemonics)


# Wrong address
@router.message(~IsWallet(), StateFilter(FSMMain.new_address))
async def process_wrong_address_input(message: Message, i18n: TranslatorRunner):
    await message.answer(text=i18n.wrong.address(),
                         reply_markup=back_kb(i18n))


# User enter
@router.message(IsMnemonics(), StateFilter(FSMMain.new_mnemonics))
async def process_mnemonics_input(message: Message, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)
    user = await r.hgetall(str(message.from_user.id))
    user[b'mnemonics'] = message.text
    await r.hmset(str(message.from_user.id), user)
    await message.answer(text=i18n.wallet.added(),
                         reply_markup=import_export_kb(i18n))
    await state.clear()


# Wrong Mnemonics
@router.message(~IsMnemonics(), StateFilter(FSMMain.new_mnemonics))
async def process_wrong_mnemonics_input(message: Message, i18n: TranslatorRunner):
    await message.answer(text=i18n.wrong.mnemonics(),
                         reply_markup=back_kb(i18n))


"""JETTONS IMPORT/EXPORT"""


# Calculate value of JETTONS by keyboard-input in jettons INPUT
@router.callback_query((F.data.in_(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])),
                       StateFilter(FSMMain.jettons_import))
async def process_pair_choice_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    try:
        await state.update_data(price=str((await state.get_data())['price'] + callback.data))
        await callback.message.edit_text(text=i18n.enter.forimport(price=str((await state.get_data())['price'])),
                                         reply_markup=digit_inline(i18n))
        await callback.answer()
        await state.set_state(FSMMain.jettons_import)
    except TelegramBadRequest:
        await callback.answer()


# Delete value of JETTONS by keyboard-input in jettons INPUT
@router.callback_query((F.data == '<'),
                       StateFilter(FSMMain.jettons_import))
async def process_pair_choice_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    try:
        await state.update_data(price=str((await state.get_data())['price'][:-1]))
        await callback.message.edit_text(text=i18n.enter.forimport(price=str((await state.get_data())['price'])),
                                         reply_markup=digit_inline(i18n))
        await callback.answer()
        await state.set_state(FSMMain.jettons_import)
    except TelegramBadRequest:
        await callback.answer()


# Calculate value of JETTONS by keyboard-input in jettons EXPORT
@router.callback_query((F.data.in_(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])),
                       StateFilter(FSMMain.jettons_export))
async def process_pair_choice_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    try:
        await state.update_data(price=str((await state.get_data())['price'] + callback.data))
        await callback.message.edit_text(text=i18n.enter.forexport(price=str((await state.get_data())['price'])),
                                         reply_markup=digit_inline(i18n))
        await callback.answer()
        await state.set_state(FSMMain.jettons_export)
    except TelegramBadRequest:
        await callback.answer()


# Delete value of JETTONS by keyboard-input in jettons INPUT
@router.callback_query((F.data == '<'),
                       StateFilter(FSMMain.jettons_export))
async def process_pair_choice_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    try:
        await state.update_data(price=str((await state.get_data())['price'][:-1]))
        await callback.message.edit_text(text=i18n.enter.forexport(price=str((await state.get_data())['price'])),
                                         reply_markup=digit_inline(i18n))
        await callback.answer()
        await state.set_state(FSMMain.jettons_export)
    except TelegramBadRequest:
        await callback.answer()


# Value of jettons entered in jettons IMPORT
@router.callback_query(F.data == 'ok', StateFilter(FSMMain.jettons_import))
async def process_enter_input_value(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    value = int((await state.get_data())['price'])

    # Cant export/import less than 50 jettons
    if value < 50:
        try:
            await callback.message.edit_text(text=i18n.need.more(),
                                             reply_markup=back_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()
    else:
        try:
            await callback.message.edit_text(text=i18n.agree.forimport(value=value),
                                             reply_markup=InlineKeyboardMarkup(
                                                 inline_keyboard=[[InlineKeyboardButton(
                                                    text=i18n.confirm.forimport(value=value),
                                                    callback_data=f'import {value}')
                                                 ]]))
            await state.set_state(FSMMain.confirm_import)
        except TelegramBadRequest:
            await callback.answer()


# Value of jettons entered in jettons EXPORT
@router.callback_query(F.data == 'ok', StateFilter(FSMMain.jettons_export))
async def process_enter_export_value(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)
    user = await r.hgetall(str(callback.from_user.id))
    value = int((await state.get_data())['price'])

    # User hasnt so muck jettons
    if value > int(str(user[b'jettons'], encoding='utf-8')):
        try:
            await callback.message.edit_text(text=i18n.notenough(),
                                             reply_markup=back_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()

    # Cant export/import less than 50 jettons
    elif value < 50:
        try:
            await callback.message.edit_text(text=i18n.need.more(),
                                             reply_markup=back_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()
    else:
        try:
            await callback.message.edit_text(text=i18n.agree.forexport(value=value),
                                             reply_markup=InlineKeyboardMarkup(
                                                 inline_keyboard=[[InlineKeyboardButton(
                                                    text=i18n.confirm.forexport(value=value),
                                                    callback_data=f'export {value}')
                                                 ]]))
            await state.set_state(FSMMain.confirm_export)
        except TelegramBadRequest:
            await callback.answer()


# Entered value is incorrect
@router.callback_query(~F.text.isdigit(), StateFilter(FSMMain.jettons_import) or StateFilter(FSMMain.jettons_export))
async def process_wrong_value(callback: CallbackQuery, i18n: TranslatorRunner):
    try:
        await callback.message.edit_text(text=i18n.wrong.value())
    except TelegramBadRequest:
        await callback.answer()


# Jettons IMPORT confirm
@router.callback_query(IsImport(), StateFilter(FSMMain.confirm_import))
async def process_confirm_import(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)

    # Vars initialization
    user = await r.hgetall(str(callback.from_user.id))
    space = callback.data.find(' ')
    value = int(callback.data[space+1:])
    mnemonics = str(user[b'mnemonics'], encoding='utf-8').split()
    balance = await check_balance(str(user[b'export_address'], encoding='utf-8'))

    # Need TONs for fee
    if balance < 100000000:
        try:
            await callback.message.edit_text(text=i18n.notenough.ton(),
                                             reply_markup=back_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()
    else:
        try:
            await jetton_import(mnemonics, value)
            await callback.message.edit_text(text=i18n.importcomplete(),
                                             reply_markup=play_account_kb(i18n))
            user[b'jettons'] = int(str(user[b'jettons'], encoding='utf-8')) + value
            await r.hmset(str(callback.from_user.id), user)
            await state.clear()
        except:
            await callback.message.edit_text(text=i18n.ERROR(),
                                             reply_markup=play_account_kb(i18n))
            await state.clear()


# Jettons EXPORT confirm
@router.callback_query(IsExport(), StateFilter(FSMMain.confirm_export))
async def procces_confirm_import(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)

    # Vars initialization
    user = await r.hgetall(str(callback.from_user.id))
    space = callback.data.find(' ')
    value = int(callback.data[space+1:])
    address = str(user[b'export_address'], encoding='utf-8')
    try:
        await jetton_export(address, value)
        await callback.message.edit_text(text=i18n.exportcomplete(),
                                         reply_markup=play_account_kb(i18n))
        user[b'jettons'] = int(str(user[b'jettons'], encoding='utf-8')) - value
        await r.hmset(str(callback.from_user.id), user)
        await state.clear()
    except:
        await callback.message.edit_text(text=i18n.ERROR(),
                                         reply_markup=play_account_kb(i18n))
        await state.clear()





