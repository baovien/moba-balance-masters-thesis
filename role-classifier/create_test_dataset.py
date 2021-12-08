import os
import gzip
import json
import numpy as np
import pandas as pd
import tqdm
pd.set_option('display.max_rows', 100)


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


results = []
seen_matches = set()
invalid = 0
count = 0
with gzip.open("../data/raw/matches_5148330922-5148330922.gz", "r") as fp:
    for line in tqdm.tqdm(fp):
        match = json.loads(line)

        if not is_valid_match(match):
            invalid += 1
            continue        
    
        match_id = match["match_id"]

        if match_id in seen_matches:
            invalid += 1
            continue
        
        
        training_samples = {
            

        }

        results.append(match["players"])
        seen_matches.add(match_id)

        
print("seen matches: {}, len samples: {}, invalid: {}".format(len(seen_matches), len(results), invalid))

with open("../data/preprocessed/matches_5148330922-5148330922.npy", "wb") as fp:
    np.save(fp, np.array(results, dtype=np.int8), allow_pickle=True)