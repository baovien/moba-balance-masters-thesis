import matplotlib.pyplot as plt
import argparse
from os import stat
import pickle
import tqdm
import torch
import numpy as np
from pprint import pprint
from game import Dota2Game, GameState, LoLGame
from model import DotaDraftModel, LoLDraftModel, RandomModel
from monte_carlo_tree_search import MCTS
from collections import defaultdict, Counter
from utils import get_picks_with_names, get_bans_with_names, idx_to_name, get_hero_pos

comp_counter = Counter()
ban_counter = Counter()
comp_counter_winner = Counter()
draft_counter = Counter()
pick_positions = np.zeros((5,5))


def load_model(model_name, game, device, vgame):
    board_size = game.get_board_size()
    action_size = game.get_action_size()
    if model_name == 'random':
        return RandomModel(board_size, action_size, device)
    
    if vgame == "dota":
        model = DotaDraftModel(board_size, action_size, device)
    elif vgame == "lol":
        model = LoLDraftModel(board_size, action_size, device)
    else:
        raise Exception("Unknown model: {}".format(model_name))

    model.load_state_dict(torch.load(model_name)["state_dict"])
    return model

def play_game(game, models, args):
    current_player = args['first_pick']

    state = game.get_init_board()
    actions = []
    pick_order = defaultdict(list)
    while True:
        canonical_board = game.get_canonical_board(state, current_player)

        mcts = MCTS(game, models[current_player], args, epsilon_greedy=None)
        root = mcts.run(models[current_player], canonical_board, to_play=current_player)
    
        action = root.select_action(temperature=1)
        if action > game.get_action_size() -1 :
            actions.append("BAN {} {}".format(current_player, idx_to_name(action - game.get_action_size(), args["game"])))
        else:
            pick_order[current_player].append(action)
            actions.append("PICK {} {}".format(current_player, idx_to_name(action, args["game"])))

        state, current_player = game.get_next_state(state, current_player, action)
        reward = game.get_reward_for_player(state, current_player)

        if reward is not None:
            pick_order_pos = [get_hero_pos(hid, args["game"]) for hid in pick_order[reward]]
            for p in range(5):
                pick_positions[p][pick_order_pos[p]] += 1

            draft_counter[str(actions)] += 1

            t0, t1 = get_picks_with_names(state, args["game"])            
            bans = get_bans_with_names(state, args["game"])
            ban_counter[bans] += 1
            comp_counter[t0] += 1
            comp_counter[t1] += 1

            if reward == 1:
                comp_counter_winner[t0] += 1
            else:
                comp_counter_winner[t1] += 1
            winner_team = reward * current_player 
            return winner_team

def get_hero_pick_rate(c):
    hero_counter = Counter()

    for k, v in c.items():
        for hid in k: 
            hero_counter[hid] += v
    
    return hero_counter


def plot_win_over_time(p1, p2):
    plt.plot(p1)
    plt.plot(p2)
    plt.show()
    plt.savefig("win_over_time.png")


if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-g','--game', help='Game', choices=["dota", "lol"], type=str, required=True)
    parser.add_argument('-d','--draft', help='Draft Type', type=str, default="captains")    
    parser.add_argument('-n','--n_games', help='Number of games', type=int, default=100)
    parser.add_argument('-s','--simulations', help='Number of simulations', type=int, default=20)
    argomants = vars(parser.parse_args())
    args = {
        'num_simulations': argomants["simulations"],         # Total number of MCTS simulations to run when deciding on a move to play
        'num_games': argomants["n_games"],    # Number of games to play
        'num_iterations': 1,
        'first_pick': 1,                # 1: player 1, -1: player 2 # Do not change this. Change models dict instead
        'draft_type': argomants["draft"],
        'game': argomants["game"]
    }

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    if args["game"] == "dota":
        game = Dota2Game(draft_type=args["draft_type"])
        model = load_model('checkpoints/alpha9/checkpoint_400.pth', game, device, args["game"])
        # model2 = load_model('checkpoints/alpha9/checkpoint_200.pth', game, device, args["game"])
    else:
        game = LoLGame(draft_type=args["draft_type"])
        model = load_model('checkpoints/loltournament_lol_tournament/checkpoint_190.pth', game, device, args["game"])
        # model2 = load_model('checkpoints/loltournament_lol_tournament/checkpoint_50.pth', game, device, args["game"])

    random_model = load_model('random', game, device, args["game"])
    models = {
        1: model,
        -1: model,
    }

    print("=" * 20 + " args " + "=" * 20)
    pprint(args)
    print("=" * 20 + " models " + "=" * 20)
    print(models)
    wins_over_time1 = []
    wins_over_time2 = []
    win_percentages = defaultdict(list)

    for i in range(args['num_iterations']):

        results = []
        result_c = Counter()
        for games in tqdm.tqdm(range(args['num_games']), desc="Games"):
            res = play_game(game, models, args)
            result_c.update([res])
            wins_over_time1.append(result_c[1])
            wins_over_time2.append(result_c[-1])

        # pprint(result_c)

        if len(result_c) == 2:
            win_p_player_1 = result_c[1] / (result_c[1] + result_c[-1])
            win_p_player_2 = result_c[-1] / (result_c[1] + result_c[-1])

            print("player 1: {:.2f}% win rate".format(win_p_player_1))
            print("player 2: {:.2f}% win rate".format(win_p_player_2))
            win_percentages[1].append(win_p_player_1)
            win_percentages[-1].append(win_p_player_2)

    # plot_win_over_time(wins_over_time1, wins_over_time2)
    print("=" * 20 + " results " + "=" * 20)

    print("# Top 5 comps:\n", comp_counter.most_common(5))
    print("# Top 8 picked heroes:\n", get_hero_pick_rate(comp_counter).most_common(8))
    print("# Least 8 common heroes picked:\n", get_hero_pick_rate(comp_counter).most_common()[:-8-1:-1])

    print("# Top 8 picked heroes winner:\n", get_hero_pick_rate(comp_counter_winner).most_common(8))
    pick_counts = get_hero_pick_rate(comp_counter)
    win_counts = get_hero_pick_rate(comp_counter_winner)
    win_rate = Counter()
    for k,v in win_counts.items():
        win_rate[k] = round(v / pick_counts[k], 2)
    
    print("Heroes with highest winrate\n", win_rate.most_common(10))

    print("Most common bans:")
    ban_counts = get_hero_pick_rate(ban_counter)
    print(ban_counts.most_common(10))

    print("Most common draft sequence")
    print(draft_counter.most_common(2))
    
    print("=" * 20 + " args " + "=" * 20)
    pprint(args)

    print("Average win %: p1 {:.2f}% vs p2 {:.2f}%".format(np.mean(win_percentages[1]) * 100, np.mean(win_percentages[-1]) * 100))
    # save draft_counter to pickle
    out_p = "results/draft_counter_{}_{}.pkl".format(args["game"], args['draft_type'])
    with open(out_p, 'wb') as f:
        pickle.dump(draft_counter, f)

    row_sums = pick_positions.sum(axis=1)
    pick_positions_normalized = pick_positions / row_sums[:, np.newaxis]
    print(pick_positions_normalized)



