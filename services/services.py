from database.database import games, users_db
from fluentogram import TranslatorRunner


# Returns key of dict by users answer as value
def normalize_answer(i18n: TranslatorRunner, user_answer: str) -> str:
    game = {'rock': i18n.rock(),
            'paper': i18n.paper(),
            'scissors': i18n.scissors()}
    for key in game:
        if game[key] == user_answer:
            print(key, game[key])
            break
    return key


# Define winner of turn
def _get_winner(player1_move: str, player2_move: str, room_id) -> str:
    rules = {'rock': 'scissors',
             'scissors': 'paper',
             'paper': 'rock'}
    if player1_move == player2_move:
        return 'nobody_won'
    elif rules[player1_move] == player2_move:
        if games[room_id]['player2_health'] > 0:
            games[room_id]['player2_health'] -= 1
            return 'player2_damaged'
        else:
            return 'player1_won'
    else:
        if games[room_id]['player1_health'] > 0:
            games[room_id]['player1_health'] -= 1
            return 'player1_damaged'
        else:
            return 'player2_won'


# Redirection of turn result
def turn_result(player1_move: str, player2_move: str, room_id, i_am: str) -> str:
    result = _get_winner(player1_move, player2_move, room_id)
    print(result)
    if result == 'nobody_won':
        return 'nobody_won'
    elif result == 'player1_damaged':
        if result[:7] == i_am:
            return 'enemy_caused_damaged'
        else:
            return 'you_caused_damage'
    elif result == 'player2_damaged':
        if result[:7] == i_am:
            return 'enemy_caused_damaged'
        else:
            return 'you_caused_damage'
    elif result == 'player1_won':
        if result[:7] == i_am:
            return 'you_win'
        else:
            return 'you_lose'
    elif result == 'player2_won':
        if result[:7] == i_am:
            return 'you_win'
        else:
            return 'you_lose'


# Changing account stats after game
def game_result(result: str, my_id: int | str, enemy_id: int | str, room_id: int | str):
    if result == 'lose':
        # Player lose
        users_db[my_id]['total_games'] += 1
        users_db[my_id]['lose'] += 1
        users_db[my_id]['jettons'] -= games[room_id]['bet']
        users_db[my_id]['rating'] = int((users_db[my_id]['win'] / users_db[my_id]['total_games']) * 1000)
        users_db[my_id]['current_game'] = None
        users_db[enemy_id]['total_games'] += 1
        users_db[enemy_id]['win'] += 1
        users_db[enemy_id]['jettons'] += (games[room_id]['bet'] + len(users_db[enemy_id]['referrals']))
        users_db[enemy_id]['rating'] = int((users_db[enemy_id]['win'] / users_db[enemy_id]['total_games']) * 1000)
        users_db[enemy_id]['current_game'] = None
    else:
        # Player wins
        users_db[my_id]['total_games'] += 1
        users_db[my_id]['win'] += 1
        users_db[my_id]['jettons'] += (games[room_id]['bet'] + len(users_db[my_id]['referrals']))
        users_db[my_id]['rating'] = int((users_db[my_id]['win'] / users_db[my_id]['total_games']) * 1000)
        users_db[my_id]['current_game'] = None
        users_db[enemy_id]['total_games'] += 1
        users_db[enemy_id]['lose'] += 1
        users_db[enemy_id]['jettons'] -= games[room_id]['bet']
        users_db[enemy_id]['rating'] = int((users_db[enemy_id]['win'] / users_db[enemy_id]['total_games']) * 1000)
        users_db[enemy_id]['current_game'] = None
