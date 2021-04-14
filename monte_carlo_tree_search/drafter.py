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
        return {
            draft.make_move(i) for i, value in enumerate(draft.tup) if value is None
        }

    def find_random_child(draft):
        if draft.terminal:
            return None  # If the game is finished then no moves can be made
        empty_spots = [i for i, value in enumerate(draft.tup) if value is None]
        return draft.make_move(choice(empty_spots))

    def reward(draft):
        if not draft.terminal:
            raise RuntimeError(f"reward called on nonterminal board {draft}")
        if draft.winner is draft.turn:
            # It's your turn and you've already won. Should be impossible.
            raise RuntimeError(f"reward called on unreachable board {draft}")
        if draft.turn is (not draft.winner):
            return 0  # Your opponent has just won. Bad.
        if draft.winner is None:
            return 0.5  # Board is a tie
        # The winner is neither True, False, nor None
        raise RuntimeError(f"board has unknown winner type {draft.winner}")

    def is_terminal(draft):
        return draft.terminal

    def make_move(draft, index):
        tup = draft.tup[:index] + (draft.turn,) + draft.tup[index + 1:]
        turn = not draft.turn
        winner = _find_winner(tup)
        is_terminal = (winner is not None) or not any(v is None for v in tup)
        return Draft(tup, turn, winner, is_terminal)

    def to_pretty_string(draft):
        radiant, dire = draft.tup[::2], draft.tup[1::2]
        radiant_heroes = map(_hero_name_by_hid, radiant)
        dire_heroes = map(_hero_name_by_hid, dire)

        return f"r: {radiant_heroes} d:{dire_heroes}\n" \
               f"r: {radiant} d: {dire}"


def play_game():
    tree = MCTS()
    draft = new_draft()
    print(draft.to_pretty_string())
    while True:
        row_col = input("enter row,col: ")
        row, col = map(int, row_col.split(","))
        index = 3 * (row - 1) + (col - 1)
        if draft.tup[index] is not None:
            raise RuntimeError("Invalid move")
        draft = draft.make_move(index)
        print(draft.to_pretty_string())
        if draft.terminal:
            break
        # You can train as you go, or only at the beginning.
        # Here, we train as we go, doing fifty rollouts each turn.
        for _ in range(50):
            tree.do_rollout(draft)
        draft = tree.choose(draft)
        print(draft.to_pretty_string())
        if draft.terminal:
            break


@lru_cache()
def _hero_name_by_hid(hid):
    heroes_path = "../data/heroes.json"
    with open(heroes_path, 'r') as fp:
        heroes = json.load(fp)

    rid = _hid_to_rid(hid)
    return heroes[rid]


@lru_cache()
def _hid_to_rid(hid):
    d_heroes_path = "../data/heroes_dict_reverse.json"
    with open(d_heroes_path, 'r') as fp:
        d_heroes = json.load(fp)

    return d_heroes[hid]


def _tup_to_draft_onehot(tup):
    """
    the tup contains heroes where every other entry is radiant dire.
    onehot draft
    """
    draft = [_hid_to_rid(x) for x in tup]
    radiant, dire = draft[::2], draft[1::2]
    oh_radiant, oh_dire = np.zeros(128, dtype=np.uint8)

    for h in radiant:
        oh_radiant[h] = -1

    for h in dire:
        oh_dire[h] = 1

    oh_draft = np.concatenate((oh_radiant, oh_dire))

    return oh_draft


def _find_winner(tup):
    "Returns None if no winner, True if Radiant wins, False if Dire wins"

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


def new_draft():
    return Draft(tup=(None,) * 10, turn=True, winner=None, terminal=False)


if __name__ == "__main__":
    print(_hero_name_by_hid("118"))
    # play_game()
