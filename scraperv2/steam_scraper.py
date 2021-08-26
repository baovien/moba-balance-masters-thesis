"""
CHECKS
===============
* Have been tagged for lane wins
* hero_id within range
* Matchtype/lobbytype = 22 - Ranked Matchmaking
* Check for 10 heroes in matches
* Remove matches with duration less than 10 minutes - duration
* Not abandoned match = players > leaver_status
    * 0 - NONE - finished match, no abandon.
    * 1 - DISCONNECTED - player DC, no abandon.
"""

import os
import csv
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
load_dotenv()

api_key = os.environ.get("STEAM_API_KEY") 

url_heroes = "https://api.opendota.com/api/heroes"
response_heroes = requests.get(url_heroes)
if (response_heroes.ok):
    print("got heroes map")
    data_heroes = json.loads(response_heroes.content.decode("utf-8"))

url_matches = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1?key=" + api_key + "&skill=3&min_players=10"
response_matches = requests.get(url_matches)
if (response_matches.ok):
    print("got match history")
    data_matches = json.loads(response_matches.content.decode("utf-8"))
    seq_nums = []
    for m in data_matches["result"]["matches"]:
        seq_nums.append(m["match_seq_num"])
    
    print(sorted(seq_nums))
    
    raise False

url_match_seq = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/v1?key=" + api_key + "&skill=3&min_players=10"
response_matches = requests.get(url_matches)
if (response_matches.ok):
    print("got match history")
    data_matches = json.loads(response_matches.content.decode("utf-8"))
    seq_nums = []
    for m in data_matches["result"]["matches"]:
        seq_nums.append(m["match_seq_num"])
    
    print(sorted(seq_nums))
    
    raise False



print("start scraping played heroes")



for i in tqdm(range(len(data_matches["result"]["matches"]))):
    time.sleep(0.5)
    match_valid = True
    match_id = data_matches["result"]["matches"][i]["match_id"]
    url_match = "http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1?key=" + api_key + "&match_id=" + str(match_id)
    response_match = requests.get(url_match)
    
    if (response_match.ok):
        match = json.loads(response_match.content.decode("utf-8"))
        for j in range(len(match["result"]["players"])):
            # check for leavers
            if match["result"]["players"][j]["leaver_status"] >= 2: 
                match_valid = False
        
        # check match dur > 20 min
        if match["result"]["duration"] < 60 * 20: 
            match_valid = False
        
        if match_valid:            
            with open('data/results.json', 'a') as fp:
                fp.write(json.dumps(match) + '\n')
