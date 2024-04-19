from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from fluentogram import TranslatorRunner

from keyboards.keyboards import game_process_kb, play_account_kb, enemy_leaved_ok
from database.database import games, users_db
from services.services import turn_result, game_result

router = Router()

"""MAIN GAME PROCESS IN ONE HANDLER"""


@router.callback_query(F.data.in_(['rock', 'paper', 'scissors']))
async def process_game_button(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner):

    # Vars initialization
    room_id = users_db[callback.from_user.id]['current_game']
    i_am = None
    enemy = None
    if games[room_id]['player1'] == callback.from_user.id:
        i_am = 'player1'
        enemy = 'player2'
    elif games[room_id]['player2'] == callback.from_user.id:
        i_am = 'player2'
        enemy = 'player1'
    move = str(i_am+'_move')
    enemy_id = int(games[room_id][enemy])

    # Setting players move
    games[room_id][move] = callback.data

    # If both players made move
    if games[room_id]['player1_move'] is not None and games[room_id]['player2_move'] is not None:

        # Checking result of turn, losers health decreasing
        result = turn_result(games[room_id]['player1_move'], games[room_id]['player2_move'],
                             room_id, i_am)

        # Checking player1 health for zero
        if games[room_id]['player1_health'] == 0:
            if i_am == 'player1':
                total_result = 'lose'
                try:

                    # Return result and return to main menu
                    await callback.message.edit_text(text=i18n.lose(),
                                                     reply_markup=play_account_kb(i18n))
                except TelegramBadRequest:
                    await callback.answer()

                # Return result to opponent and return to main menu
                await bot.send_message(chat_id=games[room_id][enemy], text=i18n.win(),
                                       reply_markup=play_account_kb(i18n))
                game_result(total_result, callback.from_user.id, enemy_id, room_id)

                # Delete game data
                del games[room_id]
            else:
                total_result = 'win'
                try:

                    # Return result and return to main menu
                    await callback.message.edit_text(text=i18n.win(),
                                                     reply_markup=play_account_kb(i18n))
                except TelegramBadRequest:
                    await callback.answer()

                # Return result to opponent and return to main menu
                await bot.send_message(chat_id=games[room_id][enemy], text=i18n.lose(),
                                       reply_markup=play_account_kb(i18n))

                # Counting total wins, loses, games, jettons
                game_result(total_result, callback.from_user.id, enemy_id, room_id)

                # Delete game data
                del games[room_id]
            await state.clear()

        # Checking player1 health for zero
        elif games[room_id]['player2_health'] == 0:
            if i_am == 'player2':
                total_result = 'lose'
                try:

                    # Return result and return to main menu
                    await callback.message.edit_text(text=i18n.lose(),
                                                     reply_markup=play_account_kb(i18n))
                except TelegramBadRequest:
                    await callback.answer()

                # Return result to opponent and return to main menu
                await bot.send_message(chat_id=games[room_id][enemy], text=i18n.win(),
                                       reply_markup=play_account_kb(i18n))
                game_result(total_result, callback.from_user.id, enemy_id, room_id)
            else:
                total_result = 'win'
                try:

                    # Return result and return to main menu
                    await callback.message.edit_text(text=i18n.win(),
                                                     reply_markup=play_account_kb(i18n))
                except TelegramBadRequest:
                    await callback.answer()

                # Return result to opponent and return to main menu
                await bot.send_message(chat_id=games[room_id][enemy], text=i18n.lose(),
                                       reply_markup=play_account_kb(i18n))
                game_result(total_result, callback.from_user.id, enemy_id, room_id)
            await state.clear()

        # If health of both players is not zero
        else:
            if result == 'you_caused_damage':
                try:

                    # Return result of turn and keyboard for next move
                    await callback.message.edit_text(text=i18n.enemy.damaged(),
                                                     reply_markup=game_process_kb(i18n))
                except TelegramBadRequest:
                    await callback.answer()

                # Return to opponent result of turn and keyboard for next move
                await bot.send_message(chat_id=games[room_id][enemy], text=i18n.you.damaged(),
                                       reply_markup=game_process_kb(i18n))
            elif result == 'enemy_caused_damaged':
                try:

                    # Return result of turn and keyboard for next move
                    await callback.message.edit_text(text=i18n.you.damaged(),
                                                     reply_markup=game_process_kb(i18n))
                except TelegramBadRequest:
                    await callback.answer()

                # Return to opponent result of turn and keyboard for next move
                await bot.send_message(chat_id=games[room_id][enemy], text=i18n.enemy.damaged(),
                                       reply_markup=game_process_kb(i18n))
            elif result == 'nobody_won':
                try:

                    # Return result of turn and keyboard for next move
                    await callback.message.edit_text(text=i18n.nobody.won(),
                                                     reply_markup=game_process_kb(i18n))
                except TelegramBadRequest:
                    await callback.answer()
                await bot.send_message(chat_id=games[room_id][enemy], text=i18n.nobody.won(),
                                       reply_markup=game_process_kb(i18n))
            games[room_id]['player1_move'] = None
            games[room_id]['player2_move'] = None

    else:

        # Suggest you wait
        try:
            await callback.message.edit_text(text=i18n.choice.made())
        except TelegramBadRequest:
            await callback.answer()


# Canceling game before by Player
@router.callback_query(F.data == 'end_game')
async def process_end_game_button(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner):

    # Vars initialization
    room_id = users_db[callback.from_user.id]['current_game']
    enemy = None
    if games[room_id]['player1'] == callback.from_user.id:
        enemy = 'player2'
    elif games[room_id]['player2'] == callback.from_user.id:
        enemy = 'player1'
    enemy_id = int(games[room_id][enemy])

    try:
        await callback.message.edit_text(text=i18n.you.leaved(),
                                         reply_markup=play_account_kb(i18n))
        await state.clear()
        users_db[callback.from_user.id]['current_game'] = None
    except TelegramBadRequest:
        await callback.answer()

    await bot.send_message(chat_id=games[room_id][enemy], text=i18n.enemy.leaved(),
                           reply_markup=enemy_leaved_ok(i18n))

    game_result('lose', callback.from_user.id, enemy_id, room_id)
    del games[room_id]

