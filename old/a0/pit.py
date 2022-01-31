from os import stat
import tqdm
import torch
import numpy as np
from pprint import pprint
from game import Dota2Game, GameState, LoLGame
from model import DotaDraftModel, RandomModel
from monte_carlo_tree_search import MCTS
from collections import Counter, defaultdict
from utils import get_picks_with_names, get_bans_with_names, get_bans_with_names_lol, get_picks_with_names_lol


def load_model(model_name, game, device):
    board_size = game.get_board_size()
    action_size = game.get_action_size()
    if model_name == 'random':
        return RandomModel(board_size, action_size, device)

    model = DotaDraftModel(board_size, action_size, device)
    model.load_state_dict(torch.load(model_name)["state_dict"])

    return model


def get_hero_pick_rate(c):
    hero_counter = Counter()

    for k, v in c.items():
        for hid in k:
            hero_counter[hid] += v

    return hero_counter


def play_game(game, players, args):
    current_player = args["first_pick"]
    state = game.get_init_board()
    winner = None
    while winner is None:
        canonical_board = game.get_canonical_board(state, current_player)
        mcts = players[current_player]["mcts"]
        model = players[current_player]["model"]
        root = mcts.run(model, canonical_board, to_play=1)
        action = root.select_action(temperature=args["temperature"])
        state, current_player = game.get_next_state(state, current_player, action)
        winner = game.get_reward_for_player(state, current_player)

    return winner * current_player, state # multiply by -1 because we have a dummy pick at the last move


if __name__ == "__main__":
    args = {
        # Total number of MCTS simulations to run when deciding on a move to play
        'num_simulations': 20,
        'num_games': 100,
        'num_iterations': 1,
        'first_pick': 1,
        'draft_type': 'tournament',
        # 'draft_type': 'captains',
        'game_type': 'lol',
        # 'game_type': 'dota',
        'epsilon_greedy': None,
        'temperature': 0,
    }

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    if args["game_type"] == "dota":
        game = Dota2Game(draft_type=args["draft_type"])
    else:
        game = LoLGame(draft_type=args["draft_type"])

    # p1_model = load_model('selected_models/a15_357.pth', game, device)
    p1_model = load_model('selected_models/lol_46.pth', game, device)
    random_model = load_model('random', game, device)

    models = {
        1: p1_model,
        -1: p1_model,
    }

    players = {
        1: {
            "model": models[1],
            "mcts": MCTS(game, models[1], args, epsilon_greedy=None)
        },
        -1: {
            "model": models[-1],
            "mcts": MCTS(game, models[-1], args, epsilon_greedy=None)
        }
    }

    print("=" * 20 + " args " + "=" * 20)
    pprint(args)
    print("=" * 20 + " models " + "=" * 20)
    print(players)

    results = Counter()

    for games in tqdm.tqdm(range(args['num_games']), desc="Games"):
        res, _ = play_game(game, players, args)
        results.update([res])

    print("p1", results[1], "\np2", results[-1])


