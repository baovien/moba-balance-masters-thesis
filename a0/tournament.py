import torch
from torch.cuda import current_blas_handle
from model import DotaDraftModel, RandomModel
from game import Dota2Game
import numpy as np
from monte_carlo_tree_search import MCTS
import tqdm
from collections import defaultdict, Counter
from pprint import pprint
from enum import Enum

def play_game(args, device):
    game = Dota2Game(draft_type=args["draft_type"])
    board_size = game.get_board_size()
    action_size = game.get_action_size()

    # model = DotaDraftModel(board_size, action_size, device)
    # model.load_state_dict(torch.load('checkpoints/checkpoint_iter_210.pth')["state_dict"])

    # model2 = DotaDraftModel(board_size, action_size, device)
    # model2.load_state_dict(torch.load('checkpoints2/checkpoint_iter_500.pth')["state_dict"])
    models = {-1: RandomModel(board_size, action_size, device), 1: RandomModel(board_size, action_size, device)}

    current_player = args['first_pick']

    state = game.get_init_board()

    while True:

        canonical_board = game.get_canonical_board(state, current_player)

        mcts = MCTS(game, models[current_player], args, epsilon_greedy=0.1)
        root = mcts.run(models[current_player], canonical_board, to_play=1)

        action_probs = [0 for _ in range(game.get_action_size())]
        for k, v in root.children.items():
            action_probs[k] = v.visit_count

        action_probs = action_probs / np.sum(action_probs)

        action = root.select_action(temperature=0)
        state, current_player = game.get_next_state(state, current_player, action)
        reward = game.get_reward_for_player(state, current_player)

        if reward is not None:
            return reward
    


if __name__ == "__main__":
    args = {
        'num_simulations': 200,  # Total number of MCTS simulations to run when deciding on a move to play
        'num_games' : 100,
        'num_iterations': 500,
        'first_pick': -1,
        'draft_type': 'school_yard'
    }

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    win_percentages = defaultdict(list)

    for i in range(args['num_iterations']):

        results = []
        result_c = Counter()
        for games in tqdm.tqdm(range(args['num_games'])):
            res = play_game(args, device)
            result_c.update([res])

        pprint(result_c)

        if len(result_c) == 2:
            win_p_player_1 = result_c[1] / (result_c[1] + result_c[-1])
            win_p_player_2 = result_c[-1] / (result_c[1] + result_c[-1]) 

            print("player 1: {:.2f}% win rate".format(win_p_player_1))
            print("player 2: {:.2f}% win rate".format(win_p_player_2))
            win_percentages[1].append(win_p_player_1)
            win_percentages[-1].append(win_p_player_2)

    print("Average win percentages for player 1: {:.2f}%".format(np.mean(win_percentages[1]) * 100))
    print("Average win percentages for player 2: {:.2f}%".format(np.mean(win_percentages[-1]) * 100))
    print(args)