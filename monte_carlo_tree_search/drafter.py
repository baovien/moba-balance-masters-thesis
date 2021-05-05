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

from tqdm import tqdm
from functools import lru_cache
from collections import namedtuple
from random import choice
from itertools import permutations

from typing import Tuple

from monte_carlo_tree_search.mcts import MCTS, EvidenceRegister, Node
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt
import pandas as pd

_TTTB = namedtuple("Draft", "tup turn winner terminal")


# Inheriting from a namedtuple is convenient because it makes the class
# immutable and predefines __init__, __repr__, __hash__, __eq__, and others
class Draft(_TTTB, Node):
    def find_children(draft):
        if draft.terminal:  # If the game is finished then no moves can be made
            return set()
        # Otherwise, you can make a move in each of the empty spots
        all_heroes = set(np.arange(0, 119))
        available_heroes = list(all_heroes - set(draft.tup))

        return {
            draft.make_move(i) for i in available_heroes
        }

    def find_random_child(draft):
        if draft.terminal:
            return None  # If the game is finished then no moves can be made

        all_heroes = set(np.arange(0, 119))
        available_heroes = list(all_heroes - set(draft.tup))
        return draft.make_move(choice(available_heroes))

    def reward(draft):
        if not draft.terminal:
            raise RuntimeError(f"reward called on nonterminal board {draft}")
        if draft.winner:
            return 1
        elif draft.winner is None:
            return 0.5
        else:
            return 0  # Your opponent has just won. Bad.

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
        is_terminal = not any(v is None for v in tup)
        winner = None
        explainer = None
        if is_terminal:
            winner = _find_winner(tup)

        # print("Turn: {}, Winner: {}, is_terminal: {}, draft: {}".format("radiant" if turn else "dire", winner, is_terminal, tup))

        return Draft(tup, turn, winner, is_terminal)

    def to_pretty_string(draft):
        radiant, dire = draft.tup[::2], draft.tup[1::2]
        radiant_heroes = [(_hero_name_by_hid(x), x) for x in radiant]
        dire_heroes = [(_hero_name_by_hid(x), x) for x in dire]

        return f"r: {radiant_heroes} d:{dire_heroes}"


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
    radiant = sorted(tup[::2], key=lambda x: x)
    dire = sorted(tup[1::2], key=lambda x: x)
    draft_oh = np.zeros(119, dtype=np.float)

    for hid in radiant:
        draft_oh[hid] = 1.

    for hid in dire:
        draft_oh[hid] = -1.

    return draft_oh.reshape(1, -1)


def rules_to_feature(rules=None, draft=None):
    # rules = {('pair_same', (104, 86)): 0,
    #          ('pair_same', (42, 49)): 1,
    #          ('pair_same', (10, 23)): 2,
    #          ('pair_same', (24, 35)): 3,
    #          ('pair_opp', (104, 11)): 4,
    #          ('pair_opp', (86, 11)): 5,
    #          ('hero', 11): 6,
    #          ('pair_same', (72, 109)): 7,
    #          ('pair_same', (54, 105)): 8}
    # draft = [[42, 49, 22, 11, 105], [104, 110, 86, 100, 89]]
    #
    # t0 = set(draft[0])
    # t1 = set(draft[1])

    t0 = set(sorted(draft[::2], key=lambda x: x))
    t1 = set(sorted(draft[1::2], key=lambda x: x))

    t0_opp_pairs = [{x, y} for x in t0 for y in t1]
    t1_opp_pairs = [{x, y} for x in t1 for y in t0]

    features = np.zeros(14161)

    for rule, rule_i in rules.items():
        r_type = rule[0]
        r_heroes = rule[1]
        if type(r_heroes) is tuple:
            r_heroes = set(r_heroes)

        if r_type == "pair_same":
            if r_heroes.issubset(t0):
                # if all(i in t0 for i in r_heroes):
                features[rule_i] = 1.

            # if all(i in t1 for i in r_heroes):
            if r_heroes.issubset(t1):
                features[rule_i] = -1.

        elif r_type == "pair_opp":
            if r_heroes in t0_opp_pairs:
                features[rule_i] = 1.

            if r_heroes in t1_opp_pairs:
                features[rule_i] = -1.

        elif r_type == "hero":
            if r_heroes in t0:
                features[rule_i] = 1.
            if r_heroes in t1:
                features[rule_i] = -1.
        else:
            raise Exception(f"No rule with type {r_type}")

    print(features[:10])


def _find_winner(tup):
    "Returns None if no winner, True if Radiant wins, False if Dire wins"

    assert not any(v is None for v in tup)

    clf = get_model()
    draft = _tup_to_draft_onehot(tup)
    y_pred = clf.predict(draft)

    coefs = clf.coefs_[-1]  # mlp coefs (n_layers - 1,) #todo

    '''
    winner = clf.predict(draft)
    
    for feature in draft/feature_set:
        if abs(feature) > 0:
            H.add(weight_k, feature_k)

    evidence = (H.top, winner)
    EvidenceRegister.register(evidence)

    '''

    evidence = (0, 1, 2, "winner")
    EvidenceRegister.register(evidence)

    if y_pred == 1:  # radiant win
        return True
    elif y_pred == 0:  # dire win
        return False

    return None


def _winner_proba(tup):
    clf = get_model()
    draft = _tup_to_draft_onehot(tup)
    return clf.predict_proba(draft)


def _keys_to_int(x):
    return {int(k): v for k, v in x.items()}


def _json_k_v_to_int(x):
    return {int(k): int(v) for k, v in x.items()}


def new_draft():
    return Draft(tup=(None,) * 10, turn=True, winner=None, terminal=False)


@lru_cache()
def get_model():
    model_path = "../models/mlp_adam_300neurons_logistic_61perc.joblib"
    # model_path = "../models/logreg_iter200_57perc.joblib"

    model = joblib.load(model_path)

    return model


def play_game():
    n_rollouts = 200
    tree = MCTS()
    draft = new_draft()

    while True:
        # You can train as you go, or only at the beginning.
        # Here, we train as we go, doing fifty rollouts each turn.
        tree.clear()

        for _ in tqdm(range(n_rollouts)):
            tree.do_rollout(draft)
        draft = tree.choose(draft)
        print(draft.to_pretty_string())

        if draft.terminal:
            print(draft.to_pretty_string())
            print(_winner_proba(draft.tup))
            print(EvidenceRegister.evidence)
            break


if __name__ == "__main__":
    # print(_hero_name_by_hid("118"))
    # print(_hid_to_rid(117))
    # play_game()
    rules_to_feature()
