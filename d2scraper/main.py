"""
https://dev.dota2.com/forum/dota-2/spectating/replays/webapi/60177-things-you-should-know-before-starting?t=58317
https://wiki.teamfortress.com/wiki/WebAPI#Dota_2
https://github.com/Arcana/node-dota2
https://api.opendota.com/api/matches/5786545933

Fetch matches for each hero
Have a record on matchid


CHECKS
===============
* Have been tagged for lane wins
* hero_id within range
* Matchtype/lobbytype = 22 - Ranked Matchmaking
* Check for 10 heroes in matches
* Remove matches with duration less than 10 minutes - duration
* Not abandonded match = players > leaver_status
    * 0 - NONE - finished match, no abandon.
    * 1 - DISCONNECTED - player DC, no abandon.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")


if __name__ == '__main__':
    print(STEAM_API_KEY)
    r = requests.get("http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1?key={}".format(STEAM_API_KEY))
    r_json = r.json()
    matches = r_json["result"]["matches"]
    print(matches[0])


