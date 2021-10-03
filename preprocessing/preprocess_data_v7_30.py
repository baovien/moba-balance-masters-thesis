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


def main():
    with open("../data/heroes.json", "r") as fp: 
        heroes = json.load(fp)
        
    df_heroes = pd.DataFrame(heroes)
    id_to_hid = df_heroes[["id"]].to_dict()["id"]
    hid_to_id = {v:k for k,v in id_to_hid.items()}

    samples = []
    seen_matches = set()

    with gzip.open("../data/raw/test_5146330922-5148330922.gz", "r") as fp:
        for line in tqdm.tqdm(fp):
            match = json.loads(line)
            players = match["players"]
            match_id = match["match_id"]
            
            # match data must contain the key match_id 
            if not "match_id" in match:
                continue
            
            # match must contain 10 players 
            if len(players) != 10:
                continue
            
            # match must be unique
            if match_id in seen_matches:
                continue
            
            # match heroids must match one of the ids in hero details
            invalid_hero_id = False

            for p in players:
                if p["hero_id"] not in hid_to_id.keys():
                    invalid_hero_id = True
                    break                
            
            if invalid_hero_id:
                continue

            seen_matches.add(match_id)
            samples.append(line)
            break
            
    print("seen matches: {}, n samples: {}".format(len(seen_matches), len(samples)))

    with open("../data/preprocessed/matches_5148330922-5148330922.npy", "wb") as fp:
        np.save(fp, np.array(samples, dtype=np.int8), allow_pickle=True)

if __name__ == "__main__":
    main()