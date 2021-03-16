import numpy as np
import itertools




heros = {41: "BaoiManzer", 40: "JaoiJJ", 1: "KneeOverToesGuy", 2: "SusanADC"}


feature_set = set()
for hero_id in heros.keys():
    feature_set.add(("hero", hero_id))

    
    for hero_opp in heros.keys():
        if hero_id == hero_opp:
            continue
            
        key = [hero_id, hero_opp]
        key.sort()
        feature_set.add(("pair_opp", tuple(key)))
        
    for hero_same in heros.keys():
        if hero_id == hero_same:
            continue
            
        key = [hero_id, hero_same]
        key.sort()
            
        feature_set.add(("pair_same", tuple(key)))
    
    
print("#feature_set:", len(feature_set))
features_to_index = {}
index_to_features = {}
for k, v in enumerate(feature_set):
    features_to_index[v] = k
    index_to_features[k] = v
    

    
game = {"team0": [40, 2], "team1": [41, 1]}


n_features = len(features_to_index)
example = np.zeros(n_features)

for team, marker in zip(game, [1, -1]):

    for h in game[team]:
        i = features_to_index[("hero", h)]
        example[i] = marker

        for h_same in game[team]:
            if h_same != h:
                key = [h, h_same]
                key.sort() 
                i_same = features_to_index[("pair_same", tuple(key))]
                example[i_same] = marker

            
    
example

index_to_features[1]











