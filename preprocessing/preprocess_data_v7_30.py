import os
import gzip
import json
import numpy as np
import pandas as pd
import tqdm

# def get_comp_by_training_sample(sample):
#     radiant_win = sample[-1]
#     radiant = []
#     dire = []
#     for i, h in enumerate(sample[:-1]):
#         if h == 1:
#             radiant.append(_get_hero_name_by_id(i))
#         elif h == -1:
#             dire.append(_get_hero_name_by_id(i))
#     print(radiant, dire, radiant_win)

# def _get_hero_name_by_id(idx: int):
#     return df_heroes[df_heroes["id"].index == idx]["localized_name"].values[0]

def is_valid_match(match):
    if not "match_id" in match:
        return False

    with open("../data/heroes.json", "r") as fp: 
        heroes = json.load(fp)

    players = match["players"]

    if len(players) != 10:
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

    hero_ids = [hero["id"] for hero in heroes]
    invalid_hero_id = False

    for p in players:
        if p["hero_id"] not in hero_ids:
            invalid_hero_id = True
            break                
    
    if invalid_hero_id:
        return False

    return True


def main():
    samples = []
    seen_matches = set()

    with gzip.open("../data/raw/test_5146330922-5148330922.gz", "r") as fp:
        for line in tqdm.tqdm(fp):
            match = json.loads(line)
            
            if not is_valid_match(match):
                continue

            match_id = match["match_id"]
            
            # match must be unique
            if match_id in seen_matches:
                continue

            seen_matches.add(match_id)
            samples.append(line)
            
    print("seen matches: {}, n samples: {}".format(len(seen_matches), len(samples)))

    with open("../data/preprocessed/matches_5148330922-5148330922.npy", "wb") as fp:
        np.save(fp, np.array(samples, dtype=np.int8), allow_pickle=True)

if __name__ == "__main__":
    main()