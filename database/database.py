# Base for new user
new_user = {
            'total_games': 0,
            'win': 0,
            'lose': 0,
            'rating': 0,
            'jettons': 15,
            'referrals': [],
            'invited': False,
            'current_game': None,
            'wallet': {
                       'export_address': None,
                       'mnemonics': None
                       }
            }

users_db = {}

# Lobby
rooms = {}

# Current games
games = {}