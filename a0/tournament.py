import torch
from torch.cuda import current_blas_handle
from model import DotaDraftModel, RandomModel
from game import Dota2Game
import numpy as np
from monte_carlo_tree_search import MCTS
import tqdm
from collections import defaultdict, Counter
from pprint import pprint
from utils import teams_to_names

comp_counter = Counter()

def load_model(model_name, game, device):

    board_size = game.get_board_size()
    action_size = game.get_action_size()
    if model_name == 'random':
        return RandomModel(board_size, action_size, device)

    model = DotaDraftModel(board_size, action_size, device)
    model.load_state_dict(torch.load(model_name)["state_dict"])
    
    return model

def play_game(game, models, args):
   
    # experiment: random v random
    # models = {-1: RandomModel(board_size, action_size, device), 1: RandomModel(board_size, action_size, device)}

    current_player = args['first_pick']

    state = game.get_init_board()

    while True:
        print(current_player)
        canonical_board = game.get_canonical_board(state, current_player)

        mcts = MCTS(game, models[current_player], args, epsilon_greedy=0.8)
        root = mcts.run(models[current_player], canonical_board, to_play=1)

        # action_probs = [0 for _ in range(game.get_action_size())]
        # for k, v in root.children.items():
        #     action_probs[k] = v.visit_count

        # action_probs = action_probs / np.sum(action_probs)

        action = root.select_action(temperature=0)
        state, current_player = game.get_next_state(state, current_player, action)
        reward = game.get_reward_for_player(state, current_player)

        if reward is not None:
            t0, t1 = teams_to_names(state)
            comp_counter[t0] += 1
            comp_counter[t1] += 1

            return reward


if __name__ == "__main__":
    # coin flip: heads: player 1, tails: player 2
    # three choices: first pick, last pick, choose side and fp, choose side and lp
    # In this implementation, player 1 picks first, and player 2 picks last
    args = {

        'num_simulations': 1,         # Total number of MCTS simulations to run when deciding on a move to play
        'num_games': 1,
        'num_iterations': 1,
        'first_pick': 1,                # 1: player 1, -1: player 2 # Do not change this. Change models dict instead
        'draft_type': 'school_yard'
    }

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    game = Dota2Game(draft_type=args["draft_type"])
    
    # experiment: two trained models
    # player_1_model = load_model('selected_models/alpha4.pth', game, device)
    # player_2_model = load_model('selected_models/alpha5.pth', game, device)

    # models = {
    #     1: player_1_model,
    #     -1: player_2_model
    # }


    models = {
        1: load_model('random', game, device),
        -1: load_model('random', game, device),
    }


    print("=" * 20 + " args " + "=" * 20)
    pprint(args)
    print("=" * 20 + " models " + "=" * 20)
    print(models)

    win_percentages = defaultdict(list)

    for i in range(args['num_iterations']):

        results = []
        result_c = Counter()
        for games in tqdm.tqdm(range(args['num_games']), desc="Games"):
            res = play_game(game, models, args)
            result_c.update([res])

        pprint(result_c)

        if len(result_c) == 2:
            win_p_player_1 = result_c[1] / (result_c[1] + result_c[-1])
            win_p_player_2 = result_c[-1] / (result_c[1] + result_c[-1])

            print("player 1: {:.2f}% win rate".format(win_p_player_1))
            print("player 2: {:.2f}% win rate".format(win_p_player_2))
            win_percentages[1].append(win_p_player_1)
            win_percentages[-1].append(win_p_player_2)

    print(comp_counter.most_common(5))

    print("=" * 20 + " results " + "=" * 20)
    print("Average win percentages for player 1: {:.2f}%".format(
        np.mean(win_percentages[1]) * 100))
    print("Average win percentages for player 2: {:.2f}%".format(
        np.mean(win_percentages[-1]) * 100))


