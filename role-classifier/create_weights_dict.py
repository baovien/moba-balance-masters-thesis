import json
import pickle
from collections import defaultdict
import numpy as np
import os

if __name__ == '__main__':
    out_path = "data/weights_dict.pkl"
    assert not os.path.exists(out_path)

    with open("data/heroes.json", "r") as fp:
        heroes = json.load(fp)

    safelane = ["Anti-Mage", "Arc Warden", "Bloodseeker", "Chaos Knight", "Clinkz", "Drow Ranger", "Faceless Void", 
    "Gyrocopter", "Juggernaut", "Lifestealer", "Luna", "Medusa", "Monkey King", "Morphling", "Naga Siren", "Phantom Assassin", 
    "Phantom Lancer", "Riki", "Slark", "Spectre", "Sven", "Terrorblade", "Tiny", "Troll Warlord", "Ursa", "Weaver", "Wraith King"]
    safelane_name_to_id = [x["id"] for x in heroes if x["localized_name"] in safelane]
    print(len(safelane), len(safelane_name_to_id))

    midlane = ["Alchemist", "Arc Warden", "Batrider", "Broodmother", "Death Prophet", "Ember Spirit", 
    "Huskar", "Invoker", "Kunkka", "Leshrac", "Lina", "Lone Druid", "Meepo", "Necrophos", "Outworld Destroyer", 
    "Puck", "Pugna", "Queen of Pain", "Razor", "Shadow Fiend", "Sniper", "Storm Spirit", 
    "Templar Assassin", "Tinker", "Viper", "Visage", "Void Spirit", "Zeus"]
    midlane_name_to_id = [x["id"] for x in heroes if x["localized_name"] in midlane]
    print(len(midlane), len(midlane_name_to_id))

    offlane = ["Axe", "Beastmaster", "Bloodseeker", "Brewmaster", "Bristleback", 
    "Centaur Warrunner", "Chaos Knight", "Dark Seer", "Dawnbreaker", "Death Prophet", "Doom", 
    "Dragon Knight", "Earthshaker", "Elder Titan", "Enigma", "Legion Commander", "Lycan", 
    "Mars", "Nature's Prophet", "Necrophos", "Night Stalker", "Pangolier", 
    "Razor", "Sand King", "Slardar", "Spirit Breaker", "Tidehunter", "Timbersaw", "Underlord", "Venomancer", "Viper"]

    offlane_name_to_id = [x["id"] for x in heroes if x["localized_name"] in offlane]
    print(len(offlane),len(offlane_name_to_id))

    soft_support = ["Bounty Hunter", "Chen", "Clockwerk", "Dark Willow", "Earth Spirit", "Earthshaker", "Enigma", 
    "Grimstroke", "Hoodwink", "Keeper of the Light", "Mirana", "Nyx Assassin", "Phoenix", "Pudge", "Rubick", 
    "Shadow Demon", "Shadow Shaman", "Silencer", "Skywrath Mage", "Snapfire", "Spirit Breaker", "Techies", 
    "Treant Protector", "Tusk", "Venomancer", "Weaver", "Windranger"]

    soft_support_name_to_id = [x["id"] for x in heroes if x["localized_name"] in soft_support]
    print(len(soft_support), len(soft_support_name_to_id))

    hard_support = ["Abaddon", "Ancient Apparition", "Bane", "Chen", "Crystal Maiden", "Dark Willow", "Dazzle", "Disruptor", 
    "Enchantress", "Grimstroke", "Io", "Jakiro", "Keeper of the Light", "Lich", "Lion", "Ogre Magi", "Omniknight", "Oracle", "Shadow Demon", 
    "Shadow Shaman", "Silencer", "Snapfire", "Treant Protector", "Vengeful Spirit", "Undying", "Warlock", "Winter Wyvern", "Witch Doctor"]
    hard_support_name_to_id = [x["id"] for x in heroes if x["localized_name"] in hard_support]
    print(len(hard_support), len(hard_support_name_to_id))


    weights_dict = defaultdict(lambda: np.zeros(5))

    for h in heroes:
        weights_dict[h["id"]] = np.array([.1, .1, .1, .1, .1])

    lane_assist = [safelane_name_to_id, midlane_name_to_id, offlane_name_to_id, soft_support_name_to_id, hard_support_name_to_id]

    for k, lane in enumerate(lane_assist):
        for hid in lane:
            weights_dict[hid][k] = 1.

    # save weights_dict to file
    with open(out_path, "wb") as fp:
        pickle.dump(dict(weights_dict), fp)

    print("done")