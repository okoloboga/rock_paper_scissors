from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.exceptions import TelegramBadRequest
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from keyboards.keyboards import create_join_kb, play_account_kb, import_export_kb, back_kb
from database.database import users_db, new_user, rooms
from filters.filters import IsReferral
from states.states import FSMMain

router = Router()

# START command
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)

    # User first time in bot - add him to DB
    if await r.exists(str(message.from_user.id)) == 0:
        await r.hmset(str(message.from_user.id), new_user)
    await message.answer_photo(photo=FSInputFile("main_menu.jpg"),
                               caption=i18n.start())
    await message.answer(text=i18n.chose.action(),
                         reply_markup=play_account_kb(i18n))



# HELP command
@router.message(Command(commands='help'))
async def process_help_command(message: Message, i18n: TranslatorRunner):
    await message.answer(text=i18n.help(),
                         reply_markup=play_account_kb(i18n))


# Canceling anything in states
@router.callback_query(F.data == 'back', ~StateFilter(default_state))
async def process_back_waiting_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)

    try:
        await callback.message.edit_text(text=i18n.start(),
                                         reply_markup=play_account_kb(i18n))
        user = await r.hgetall(str(callback.from_user.id))
        user[b'current_game'] = 0
        await r.hmset(str(callback.from_user.id), user)
        if await r.exists("r_" + str(callback.from_user.id)) != 0:
            await r.delete("r_" + str(callback.from_user.id))
    except TelegramBadRequest:
        await callback.answer()
    await state.clear()


# PLAY button pressing
@router.callback_query(F.data == 'play')
async def process_play_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    try:
        await callback.message.edit_text(text=i18n.ready(),
                                         reply_markup=create_join_kb(i18n))
        await state.clear()
    except TelegramBadRequest:
        await callback.answer()



# ACCOUNT button pressing
@router.callback_query(F.data == 'account')
async def process_account_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)

    try:
        user = await r.hgetall(str(callback.from_user.id))
        print(user)
        await callback.message.edit_text(
            text=i18n.statistic(total_games=str(user[b'total_games'], encoding='utf-8'),
                                win=str(user[b'win'], encoding='utf-8'),
                                lose=str(user[b'lose'], encoding='utf-8'),
                                rating=str(user[b'rating'], encoding='utf-8'),
                                jettons=str(user[b'jettons'], encoding='utf-8'),
                                referrals=str(user[b'referrals'], encoding='utf-8')
                                ),
            reply_markup=import_export_kb(i18n))
        await state.clear()
    except TelegramBadRequest:
        await callback.answer()


# REFCODE button pressing
@router.callback_query(F.data == 'get_refcode')
async def process_get_refcode_button(callback: CallbackQuery, i18n: TranslatorRunner):
    try:
        await callback.message.edit_text(text=f'{hex(callback.from_user.id)}',
                                         reply_markup=import_export_kb(i18n))
    except TelegramBadRequest:
        await callback.answer()


# BACK button pressing without states
@router.callback_query(F.data == 'back')
async def process_back_button(callback: CallbackQuery, i18n: TranslatorRunner):
    try:
        await callback.message.edit_text(text=i18n.start(id=callback.from_user.id),
                                         reply_markup=play_account_kb(i18n))
    except TelegramBadRequest:
        await callback.answer()


# ENTER REFCODE button pressing
@router.callback_query(F.data == 'enter_code')
async def process_enter_code_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)

    user = await r.hgetall(str(callback.from_user.id))
    if str(user[b'invited'], encoding='utf-8') == '0':
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


# RECODE entered - processing
@router.message(IsReferral(), StateFilter(FSMMain.enter_code))
async def process_checking_referral_code(message: Message, state: FSMContext, i18n: TranslatorRunner):
    r = aioredis.Redis(host='localhost', port=6379)

    user = await r.hgetall(str(message.from_user.id))
    parent = await r.hgetall(str(int(message.text, 16)))
    if await r.exists(str(int(message.text, 16))) == 0:
        await message.answer(text=i18n.doesnt.exist(),
                             reply_markup=back_kb(i18n))
    elif int(message.text, 16) == message.from_user.id:
        await message.answer(text=i18n.cant.invite.yourself(),
                             reply_markup=back_kb(i18n))
    elif int(message.from_user.id) == str(parent[b'invited'], encoding='utf-8'):
        await message.answer(text=i18n.cant.invited.by.invited(),
                             reply_markup=back_kb(i18n))
    else:
        parent[b'referrals'] = int(str(parent[b'referrals'], encoding='utf-8')) + 1
        parent[b'jettons'] = int(str(parent[b'jettons'], encoding='utf-8')) + 10
        user[b'jettons'] = int(str(user[b'jettons'], encoding='utf-8')) + 10
        user[b'invited'] = int(message.text, 16)
        await r.hmset(str(message.from_user.id), user)
        await r.hmset(str(int(message.text, 16)), parent)
        await message.answer(text=i18n.referral.complete(),
                             reply_markup=play_account_kb(i18n))
        await state.clear()


# Incorrect refcode
@router.message(StateFilter(FSMMain.enter_code))
async def process_checking_referral_code(message: Message, state: FSMContext, i18n: TranslatorRunner):
    await message.answer(text=i18n.incorrect.code(),
                         reply_markup=import_export_kb(i18n))
    await state.clear()

