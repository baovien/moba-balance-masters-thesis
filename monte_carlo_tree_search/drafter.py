"""
An example implementation of the abstract Node class for use in MCTS

If you run this file then you can play against the computer.

A tic-tac-toe board is represented as a tuple of 9 values, each either None,
True, or False, respectively meaning 'empty', 'X', and 'O'.

The board is indexed by row:
0 1 2
3 4 5
6 7 8

For example, this game board
O - X
O X -
X - -
corrresponds to this tuple:
(False, None, True, False, True, None, True, None, None)
"""

import json
import joblib
import numpy as np

from functools import lru_cache
from collections import namedtuple
from random import choice
from monte_carlo_tree_search.mcts import MCTS, Node

_TTTB = namedtuple("Draft", "tup turn winner terminal")


# Inheriting from a namedtuple is convenient because it makes the class
# immutable and predefines __init__, __repr__, __hash__, __eq__, and others
class Draft(_TTTB, Node):
    def find_children(draft):
        if draft.terminal:  # If the game is finished then no moves can be made
            return set()
        # Otherwise, you can make a move in each of the empty spots
        all_heroes = set(np.arange(0, 119))
        empty_spots = list(all_heroes - set(draft.tup))

        return {
            draft.make_move(i) for i in empty_spots
        }

    def find_random_child(draft):
        if draft.terminal:
            return None  # If the game is finished then no moves can be made

        all_heroes = set(np.arange(0, 119))
        empty_spots = list(all_heroes - set(draft.tup))
        return draft.make_move(choice(empty_spots))

    def reward(draft):
        if not draft.terminal:
            raise RuntimeError(f"reward called on nonterminal board {draft}")
        if draft.winner:
            return 1
        elif draft.winner is None:
            return 0.5
        else:
            return 0  # Your opponent has just won. Bad.
        #
        # # The winner is neither True, False, nor None
        # raise RuntimeError(f"board has unknown winner type {draft.winner}")

    def is_terminal(draft):
        return draft.terminal

    def make_move(draft, hid):

        next_hero_spot = None

        for i in range(0, 10):
            if draft.tup[i] is None:
                next_hero_spot = i

        assert next_hero_spot is not None

        tup = draft.tup[:next_hero_spot] + (hid,) + draft.tup[next_hero_spot + 1:]
        turn = not draft.turn
        winner = _find_winner(tup)
        is_terminal = (winner is not None) or not any(v is None for v in tup)
        # print("Turn: {}, Winner: {}, is_terminal: {}, draft: {}".format("radiant" if turn else "dire", winner, is_terminal, tup))

        return Draft(tup, turn, winner, is_terminal)

    def to_pretty_string(draft):
        radiant, dire = draft.tup[::2], draft.tup[1::2]
        radiant_heroes = [_hero_name_by_hid(x) for x in radiant]
        dire_heroes = [_hero_name_by_hid(x) for x in dire]

        return f"r: {radiant_heroes} d:{dire_heroes}\n" \
               f"r: {radiant} d: {dire}"


@lru_cache()
def _hid_to_rid(hid):
    d_heroes_path = "../data/hid_to_rid_dict.json"
    with open(d_heroes_path, 'r') as fp:
        d_heroes = json.load(fp)
        d_heroes = _json_k_v_to_int(d_heroes)

    return d_heroes[hid]


@lru_cache()
def _hero_name_by_hid(hid):
    if hid is None:
        return None

    heroes_path = "../data/heroes.json"
    with open(heroes_path, 'r') as fp:
        heroes = json.load(fp)
        heroes = _keys_to_int(heroes)

    rid = _hid_to_rid(hid)
    return heroes[rid]


def _tup_to_draft_onehot(tup):
    """
    the tup contains heroes where every other entry is radiant dire.
    onehot draft
    """
    radiant, dire = tup[::2], tup[1::2]
    draft_oh = np.zeros(119, dtype=np.float)

    for hid in radiant:
        draft_oh[hid] = 1.

    for hid in dire:
        draft_oh[hid] = -1.

    return draft_oh.reshape(1, -1)


def _find_winner(tup):
    "Returns None if no winner, True if Radiant wins, False if Dire wins"

    if any(v is None for v in tup):
        return None

    # predict winner with MLP model
    model_path = "../models/mlp_adam_300neurons_logistic_61perc.joblib"
    clf = joblib.load(model_path)
    draft = _tup_to_draft_onehot(tup)
    y_pred = clf.predict(draft)
    if y_pred == 1:  # radiant win
        return True
    elif y_pred == 0:  # dire win
        return False

    return None


def _winner_proba(tup):
    model_path = "../models/mlp_adam_300neurons_logistic_61perc.joblib"
    clf = joblib.load(model_path)
    draft = _tup_to_draft_onehot(tup)
    return clf.predict_proba(draft)


def _keys_to_int(x):
    return {int(k): v for k, v in x.items()}


def _json_k_v_to_int(x):
    return {int(k): int(v) for k, v in x.items()}


def new_draft():
    return Draft(tup=(None,) * 10, turn=True, winner=None, terminal=False)


def play_game():
    tree = MCTS()
    draft = new_draft()
    while True:
        # You can train as you go, or only at the beginning.
        # Here, we train as we go, doing fifty rollouts each turn.
        for _ in range(1000):
            tree.do_rollout(draft)
        draft = tree.choose(draft)
        print(draft.to_pretty_string())
        if draft.terminal:
            print(_winner_proba(draft.tup))
            break


if __name__ == "__main__":
    # print(_hero_name_by_hid("118"))
    # print(_hid_to_rid(117))
    play_game()
