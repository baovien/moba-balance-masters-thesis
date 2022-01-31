from os import stat
from numpy.random import random
import tqdm
import torch
import numpy as np
from pprint import pprint
from game import Dota2Game, GameState, LoLGame
from model import DotaDraftModel, RandomModel
from monte_carlo_tree_search import MCTS
from collections import Counter, defaultdict
from utils import get_picks_with_names, get_bans_with_names, get_bans_with_names_lol, get_picks_with_names_lol

comp_counter = Counter()
team_comps = defaultdict(Counter)
ban_counter = Counter()
comp_counter_winner = Counter()
fp_wins = Counter()
radiant_wins = Counter()

def load_model(model_name, game, device):
    board_size = game.get_board_size()
    action_size = game.get_action_size()
    if model_name == 'random':
        return RandomModel(board_size, action_size, device)

    model = DotaDraftModel(board_size, action_size, device)
    model.load_state_dict(torch.load(model_name)["state_dict"])
    
    return model

def play_game(game, models, args):
    player_order = []
    
    current_player = args['first_pick']

    state = game.get_init_board()
    while True:
        player_order.append(current_player)
        canonical_board = game.get_canonical_board(state, current_player)

        mcts = MCTS(game, models[current_player], args, epsilon_greedy=args["epsilon_greedy"])
        root = mcts.run(models[current_player], canonical_board, to_play=1)
        action = root.select_action(temperature=args["temperature"])
        state, current_player = game.get_next_state(state, current_player, action)
        reward = game.get_reward_for_player(state, current_player)
        if reward is not None:
            if args["game_type"] == "dota":
                t0, t1 = get_picks_with_names(state)            
                bans = get_bans_with_names(state)
            else:
                t0, t1 = get_picks_with_names_lol(state)            
                bans = get_bans_with_names_lol(state)


            fp_lp = GameState.first_pick(state)
            is_radiant = GameState.radiant_player(state)
            
            team_comps["t0"][t0] += 1
            team_comps["t1"][t1] += 1
            fp_wins[fp_lp] += 1 
            radiant_wins[is_radiant] += 1
            ban_counter[bans] += 1
            comp_counter[t0] += 1
            comp_counter[t1] += 1

            if reward == 1:
                comp_counter_winner[t0] += 1
            else:
                comp_counter_winner[t1] += 1

            # ret.append((hist_state, hist_action_probs, reward * ((-1) ** (hist_current_player != current_player))))
            return reward

def get_hero_pick_rate(c):
    hero_counter = Counter()

    for k, v in c.items():
        for hid in k: 
            hero_counter[hid] += v
    
    return hero_counter

if __name__ == "__main__":
    # coin flip: heads: player 1, tails: player 2
    # three choices: first pick, last pick, choose side and fp, choose side and lp
    # In this implementation, player 1 picks first, and player 2 picks last
    args = {
        'num_simulations': 5,         # Total number of MCTS simulations to run when deciding on a move to play
        'num_games': 250,
        'first_pick': 1,                # 1: player 1, -1: player 2 # Do not change this. Change models dict instead
        # 'draft_type': 'tournament',
        'draft_type': 'captains',
        # 'game_type': 'lol',
        'game_type': 'dota',
        'epsilon_greedy': None, 
        'temperature': 0,
    }

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
      
    if args["game_type"] == "dota":
        game = Dota2Game(draft_type=args["draft_type"])
    else:
        game = LoLGame(draft_type=args["draft_type"])

    
    # alpha15 = load_model('checkpoints/alpha15_dota_captains/checkpoint_150.pth', game, device)
    # delta2 = load_model('checkpoints/delta2/delta2_1800.pth', game, device)
    a16 = load_model('checkpoints/alpha16_dota_captains/checkpoint_290.pth', game, device)


    random_model = load_model('random', game, device)

    player1 = a16
    player2 = a16

    print("=" * 20 + " args " + "=" * 20)
    pprint(args)

    result_c = Counter()

    for i in [1, -1]:
        winners_local = Counter()
        p1 = i
        p2 = -i
        print(p1, p2)
        models = {
            p1: player1,
            p2: player2,
        }
        print("=" * 20 + " models " + "=" * 20)
        print(models)

        for games in tqdm.tqdm(range(args['num_games']), desc="Games"):
            res = play_game(game, models, args)
            winners_local[res] += 1


        print("=" * 20 + " win_percentages " + "=" * 20)
        print("{}: {} | {} {}".format(
            p1,
            winners_local[p1] / (winners_local[p1] + winners_local[p2]), 
            p2,
            winners_local[p2] / (winners_local[p1] + winners_local[p2])))
        print(winners_local)
        result_c[1] += winners_local[p1]
        result_c[-1] += winners_local[p2]

    print("=" * 20 + " results " + "=" * 20)

    print("====== Top 5 comps:\n", comp_counter.most_common(5))
    print("====== Top 8 picked heroes:\n", get_hero_pick_rate(comp_counter).most_common(8))
    print("====== Top 8 picked heroes winner:\n", get_hero_pick_rate(comp_counter_winner).most_common(8))
    pick_counts = get_hero_pick_rate(comp_counter)
    win_counts = get_hero_pick_rate(comp_counter_winner)
    win_rate = Counter()
    for k,v in win_counts.items():
        win_rate[k] = round(v / pick_counts[k], 2)
    
    print("====== Win rate", win_rate.most_common(5))
    ban_counts = get_hero_pick_rate(ban_counter)
    print("====== Top 10 bans:\n", ban_counts.most_common(5))
    print("====== team comps 1:\n", team_comps["t0"].most_common(5))
    print("====== team comps 2:\n", team_comps["t1"].most_common(5))

    print()
    print("====== Average win %: p1 {:.2f}% vs p2 {:.2f}%".format(result_c[1] / (result_c[1] + result_c[-1]) * 100, result_c[-1] / (result_c[1] + result_c[-1]) * 100))