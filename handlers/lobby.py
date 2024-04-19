from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from fluentogram import TranslatorRunner

from keyboards.keyboards import (back_kb, create_join_kb, select_enemy,
                                 game_process_kb, bet_kb, play_account_kb)
from database.database import rooms, games, users_db
from states.states import FSMMain
from filters.filters import IsEnemy

router = Router()

"""GAME LOBBY: CREATE OR JOIN"""


# CREATE button pressing
@router.callback_query(F.data == 'create', StateFilter(default_state))
async def process_create_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):

    # Checking for existing games of this player
    if users_db[callback.from_user.id]['current_game'] is not None:
        try:
            await callback.message.edit_text(text=i18n.already.ingame(),
                                             reply_markup=play_account_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()
    else:
        try:
            await callback.message.edit_text(text=i18n.bet(),
                                             reply_markup=bet_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()
        await state.set_state(FSMMain.make_bet)


# BET selected by pressing button
@router.callback_query(F.data.in_(['b1', 'b2', 'b3', 'b4', 'b5', 'b25']), StateFilter(FSMMain.make_bet))
async def process_yes_answer(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):

    # Parsing for value of bet
    bet = int(callback.data[1]) if len(callback.data) != 3 else int(callback.data[1:3])

    # If player have not enough jettons
    if bet > users_db[callback.from_user.id]['jettons']:
        await callback.message.edit_text(text=i18n.notenough(),
                                         reply_markup=bet_kb(i18n))
    else:

        # Creating new room
        rooms[callback.from_user.id] = {'user_id': callback.from_user.id, 'bet': bet}

        # Setting flag of waiting for game
        users_db[callback.from_user.id]['current_game'] = callback.from_user.id
        try:
            await callback.message.edit_text(text=i18n.yes.wait(),
                                             reply_markup=back_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()
        await state.set_state(FSMMain.wait_game)


# WAIT button pressing
@router.callback_query(F.data == 'wait', StateFilter(FSMMain.wait_game))
async def process_wait_button(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):

    # Checking for update of game start
    if callback.from_user.id in games:
        try:
            await callback.message.edit_text(text=i18n.rules(),
                                             reply_markup=game_process_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()
        await state.set_state(FSMMain.in_game)
    else:
        try:
            await callback.message.edit_text(text=i18n.still.wait(),
                                             reply_markup=back_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()


# JOIN button pressing
@router.callback_query(F.data == 'join', StateFilter(default_state))
async def process_yes_answer(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):

    # Checking for existing games of this player
    if users_db[callback.from_user.id]['current_game'] is not None:
        try:
            await callback.message.edit_text(text=i18n.already.ingame(),
                                             reply_markup=play_account_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()
    else:

        # If no games
        if len(rooms) == 0:
            try:
                await callback.message.edit_text(text=i18n.you.first(),
                                                 reply_markup=create_join_kb(i18n))
            except TelegramBadRequest:
                await callback.answer()
        else:
            try:
                await callback.message.edit_text(text=i18n.select.enemy(),
                                                 reply_markup=select_enemy(rooms, i18n))
            except TelegramBadRequest:
                await callback.answer()
            await state.set_state(FSMMain.select_enemy)


# Checking update for Enemy base (enemy+space+bet_value)
@router.callback_query(IsEnemy(), StateFilter(FSMMain.select_enemy))
async def select_enemy_button(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner):

    # Vars initialization
    space = callback.data.find(' ')
    id = callback.data[:space]
    bet = int(callback.data[space+1:])

    # Player select himself
    if int(callback.from_user.id) == int(id):
        try:
            await callback.message.edit_text(text=i18n.self(),
                                             reply_markup=select_enemy(rooms, i18n))
        except TelegramBadRequest:
            await callback.answer()

    # Chosen game ended or started with another player already
    elif int(id) not in rooms:
        try:
            await callback.message.edit_text(text=i18n.no.game(),
                                             reply_markup=select_enemy(rooms, i18n))
        except TelegramBadRequest:
            await callback.answer()

    # Player have not enough jettons to make current bet
    elif bet > users_db[callback.from_user.id]['jettons']:
        try:
            await callback.message.edit_text(text=i18n.notenough(),
                                             reply_markup=select_enemy(rooms, i18n))
        except TelegramBadRequest:
            await callback.answer()

    # All is greate, game starts
    else:
        room_id = int(callback.data[0:(callback.data.find(' '))])
        users_db[callback.from_user.id]['current_game'] = room_id
        games[room_id] = {room_id: 'player1',
                          callback.from_user.id: 'player2',
                          'player1': room_id,
                          'player2': callback.from_user.id,
                          'bet': rooms[room_id]['bet'],
                          'player1_move': None,
                          'player2_move': None,
                          'player1_health': 2,
                          'player2_health': 2,
                          'player1_msg_id': None,
                          'player2_msg_id': None}

        # Deleting waiting/lobby room
        del rooms[room_id]
        try:
            await callback.message.edit_text(text=i18n.rules(),
                                             reply_markup=game_process_kb(i18n))
        except TelegramBadRequest:
            await callback.answer()

        # Bot sends message to opponent for start game
        await bot.send_message(chat_id=room_id,
                               text=i18n.rules(),
                               reply_markup=game_process_kb(i18n))


