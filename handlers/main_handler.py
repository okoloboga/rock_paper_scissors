from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter

from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.exceptions import TelegramBadRequest

from copy import deepcopy

from fluentogram import TranslatorRunner

from keyboards.keyboards import create_join_kb, play_account_kb, import_export_kb, back_kb
from database.database import users_db, new_user, rooms
from filters.filters import IsReferral
from states.states import FSMMain

router = Router()


# START command
@router.message(CommandStart())
async def process_start_command(message: Message, i18n: TranslatorRunner):

    # User first time in bot - add him to DB
    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = deepcopy(new_user)
    await message.answer_photo(photo=FSInputFile("main_menu.jpg"),
                               caption=i18n.start(),
                               reply_markup=play_account_kb(i18n))


# HELP command
@router.message(Command(commands='help'))
async def process_help_command(message: Message, i18n: TranslatorRunner):
    await message.answer(text=i18n.help(),
                         reply_markup=play_account_kb(i18n))


# Canceling anything in states
@router.callback_query(F.data == 'back', ~StateFilter(default_state))
async def process_back_waiting_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    try:
        await callback.message.edit_text(text=i18n.start(),
                                         reply_markup=play_account_kb(i18n))
        users_db[callback.from_user.id]['current_game'] = None
        if callback.from_user.id in rooms:
            del rooms[callback.from_user.id]
    except TelegramBadRequest:
        await callback.answer()
    await state.clear()


# PLAY button pressing
@router.callback_query(F.data == 'play')
async def process_play_button(callback: CallbackQuery, i18n: TranslatorRunner):
    try:
        await callback.message.edit_text(text=i18n.ready(),
                                         reply_markup=create_join_kb(i18n))
    except TelegramBadRequest:
        await callback.answer()


# ACCOUNT button pressing
@router.callback_query(F.data == 'account')
async def process_account_button(callback: CallbackQuery, i18n: TranslatorRunner):
    try:
        await callback.message.edit_text(
            text=i18n.statistic(total_games=users_db[callback.from_user.id]['total_games'],
                                win=users_db[callback.from_user.id]['win'],
                                lose=users_db[callback.from_user.id]['lose'],
                                rating=users_db[callback.from_user.id]['rating'],
                                jettons=users_db[callback.from_user.id]['jettons'],
                                referrals=len(users_db[callback.from_user.id]['referrals'])
                                ),
            reply_markup=import_export_kb(i18n))
    except TelegramBadRequest:
        await callback.answer()


# Обработка нажатия кнопки Рефералльный код
@router.callback_query(F.data == 'get_refcode')
async def process_get_refcode_button(callback: CallbackQuery, i18n: TranslatorRunner):
    try:
        await callback.message.edit_text(text=f'{hex(callback.from_user.id)}',
                                         reply_markup=import_export_kb(i18n))
    except TelegramBadRequest:
        await callback.answer()


# Обработка нажатия кнопки Назад, возвращает в главное меню
@router.callback_query(F.data == 'back')
async def process_back_button(callback: CallbackQuery, i18n: TranslatorRunner):
    try:
        await callback.message.edit_text(text=i18n.start(id=callback.from_user.id),
                                         reply_markup=play_account_kb(i18n))
    except TelegramBadRequest:
        await callback.answer()


# Обработка нажатия Ввести Код
@router.callback_query(F.data == 'enter_code')
async def process_enter_code_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    if users_db[callback.from_user.id]['invited'] is False:
        try:
            await callback.message.edit_text(text=i18n.enter.referral())
            await state.set_state(FSMMain.enter_code)
        except TelegramBadRequest:
            await callback.answer()
    else:
        try:
            await callback.message.edit_text(text=i18n.already.entered(),
                                             reply_markup=play_account_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()


# Обработка ввода реферрального кода
@router.message(IsReferral(), StateFilter(FSMMain.enter_code))
async def process_checking_referral_code(message: Message, state: FSMContext, i18n: TranslatorRunner):
    if int(message.text, 16) not in users_db:
        await message.answer(text=i18n.doesnt.exist(),
                             reply_markup=back_kb(i18n))
    elif int(message.text, 16) == message.from_user.id:
        await message.answer(text=i18n.cant.invite.yourself(),
                             reply_markup=back_kb(i18n))
    elif int(message.from_user.id) == int(users_db[int(message.text, 16)]['invited']):
        await message.answer(text=i18n.cant.invited.by.invited(),
                             reply_markup=back_kb(i18n))
    else:
        users_db[int(message.text, 16)]['referrals'].append(message.from_user.id)
        users_db[int(message.text, 16)]['jettons'] += 10
        users_db[message.from_user.id]['jettons'] += 10
        users_db[message.from_user.id]['invited'] = int(message.text, 16)
        await message.answer(text=i18n.referral.complete(),
                             reply_markup=play_account_kb(i18n))
        await state.clear()


# Обработка неверного реферрального кода
@router.message(StateFilter(FSMMain.enter_code))
async def process_checking_referral_code(message: Message, state: FSMContext, i18n: TranslatorRunner):
    await message.answer(text=i18n.incorrect.code(),
                         reply_markup=import_export_kb(i18n))
    await state.clear()

