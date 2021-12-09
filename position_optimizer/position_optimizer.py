import os
import json
import numpy as np
import pickle 
import tqdm
from scipy import sparse
from collections import defaultdict
from pprint import pprint
from collections import Counter
from itertools import permutations

class PositionOptimizer:
    def __init__(self, clfs_path='data/clfs/logreg_clfs_all.pkl') -> None:
        self.opendota_data = {}
        self.clfs = defaultdict(list)
        self.role_counts = defaultdict(dict)
        self.hero_data = {}

        self._load_clfs(clfs_path)
        self._load_hero_data()
        self._load_opendota_data()
        self.hid_to_name = {h["id"]: h["localized_name"] for h in self.hero_data}

    def find_optimal_roles(self, match):
        players = match["players"]
        t0 = [p for p in players if p["player_slot"] < 128]
        t1 = [p for p in players if p["player_slot"] >= 128]

        for team in [t0, t1]:
            # !Ranks
            attributes = ["gold_per_min", "xp_per_min", "kills", "deaths", "assists", "last_hits", "hero_damage", "tower_damage"]
            ranks = {attr: sorted([(p["hero_id"], p[attr]) for p in team], key=lambda x: x[1], reverse=True) for attr in attributes}
            hids = [p["hero_id"] for p in team]
            team_position_proba = defaultdict(list)

            # !Create c
            for p in team:
                features = []
                hid = p["hero_id"]

                teammates = np.zeros((136))
                for team_hid in hids:
                    if team_hid != hid:
                        teammates[team_hid] = 1.
                
                features.append(teammates)
                
                for rank in ranks: 
                    r = ranks[rank].index((hid, p[rank]))
                    features.append(self._get_rank(r))

                x = np.concatenate(features)
                y_pred = self.clfs[hid].predict_log_proba(x.reshape(1, -1))
                updated_y_pred = self._remove_unplayed_roles(hid, y_pred.ravel())         
                team_position_proba[hid] = updated_y_pred

            best_log_p = -np.inf
            best_comp = None

            # Optimal 
            for comp in permutations(range(5), 5):
                comp_with_heroid = [(comp[i], self.hid_to_name[hid], round(team_position_proba[hid][comp[i]], 2)) for i, hid in enumerate(hids)]
                log_p = np.array([team_position_proba[hid][comp[i]] for i, hid in enumerate(hids)]).sum()
                if log_p > best_log_p:
                    best_log_p = log_p
                    best_comp = sorted(comp_with_heroid, key=lambda x: x[0])
        
            # Greedy            

            # break
                # arg_max = np.argmax(team_position_proba[hid])
                
            # argmax team_position_proba
            # sett alt annet en pos til -inf



            print("{} => {:.2f}".format(best_comp, best_log_p))

        # Return both teams
        return best_comp, best_log_p

    def _remove_unplayed_roles(self, hid, y_pred, threshold=200):
        ys = self.opendota_data["ys"]
        role_counts = dict(Counter(ys[hid]))
        updated_y_pred = np.zeros(y_pred.shape)

        for k in range(0,5):
            if role_counts[k + 1] < threshold:
                updated_y_pred[k] = -1000.
            else:
                updated_y_pred[k] = y_pred[k]
        return updated_y_pred

    def _get_rank(self, rank):
        oh = np.zeros(5)
        oh[rank] = 1
        return oh

    def _load_clfs(self, clf_path):
        """
        Load clfs from pickle file
        """
        with open(clf_path, 'rb') as f:
            self.clfs = pickle.load(f)

    def _load_opendota_data(self) -> None:
        """
        Load opendota data from data/opendota_data.json
        """
        with open('data/dataset_positions_all.pkl', 'rb') as f:
            self.opendota_data = pickle.load(f)


    def _load_hero_data(self) -> None:
        """
        Load hero data from data/heroes.json
        """
        with open('data/heroes.json', 'r') as f:
            self.hero_data = json.load(f)

def is_valid_match(match):
    if "match_id" not in match:
        return False
    if not match["lobby_type"] in {0, 5, 6, 7}:
        print("Invalid lobby type:", match["lobby_type"])
        return False
    if match["duration"] < 60 * 20:
        print("Invalid duration:", match["duration"])
        return False
    if not match["game_mode"] in {1, 2, 16, 22}:
        print("Invalid game mode:", match["game_mode"])
        return False

    return True

if __name__ == '__main__':
    po = PositionOptimizer()

    with open("data/steam_api_match_example.json", "r") as f:
        match = json.load(f)
        match = match["result"]

    if is_valid_match(match):
        comp, log_p = po.find_optimal_roles(match)
        pprint(comp)
        print(log_p)
    
