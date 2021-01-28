"""
https://dev.dota2.com/forum/dota-2/spectating/replays/webapi/60177-things-you-should-know-before-starting?t=58317
https://wiki.teamfortress.com/wiki/WebAPI#Dota_2
https://github.com/Arcana/node-dota2
https://api.opendota.com/api/matches/5786545933
https://github.com/kronusme/dota2-api

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
from pprint import pprint
from dotenv import load_dotenv


def extract_params(raw_params):
    return "".join(
        ["&{}={}".format(p_name, p_value) for p_name, p_value in raw_params.items() if p_value is not None])


class Scraper:
    def __init__(self, API_KEY):
        self.STEAM_API_KEY = API_KEY

    def get_match_details(self, match_id: str):
        """
        Information about a particular match.

        :param match_id: match id
        :return:
        result
            players
                List of players in the match.
            account_id
                32-bit account ID
            player_slot
                See #Player Slot below.
            hero_id
                The hero's unique ID. A list of hero IDs can be found via the GetHeroes method.
            item_0
                ID of the top-left inventory item.
            item_1
                ID of the top-center inventory item.
            item_2
                ID of the top-right inventory item.
            item_3
                ID of the bottom-left inventory item.
            item_4
                ID of the bottom-center inventory item.
            item_5
                ID of the bottom-right inventory item.
            kills
                The amount of kills attributed to this player.
            deaths
                The amount of times this player died during the match.
            assists
                The amount of assists attributed to this player.
            leaver_status
                0 - NONE - finished match, no abandon.
                1 - DISCONNECTED - player DC, no abandon.
                2 - DISCONNECTED_TOO_LONG - player DC > 5min, abandoned.
                3 - ABANDONED - player DC, clicked leave, abandoned.
                4 - AFK - player AFK, abandoned.
                5 - NEVER_CONNECTED - player never connected, no abandon.
                6 - NEVER_CONNECTED_TOO_LONG - player took too long to connect, no abandon.
            last_hits
                The amount of last-hits the player got during the match.
            denies
                The amount of denies the player got during the match.
            gold_per_min
                The player's overall gold/minute.
            xp_per_min
                The player's overall experience/minute.
            additional_units
                Additional playable units owned by the player. (only present if there is another unit owned by the player (?))
                unitname
                    The name of the unit
                item_0
                    ID of the top-left inventory item.
                item_1
                    ID of the top-center inventory item.
                item_2
                    ID of the top-right inventory item.
                item_3
                    ID of the bottom-left inventory item.
                item_4
                    ID of the bottom-center inventory item.
                item_5
                    ID of the bottom-right inventory item.
            season
                The season the game was played in.
            radiant_win
                Dictates the winner of the match, true for radiant; false for dire.
            duration
                The length of the match, in seconds since the match began.
                pre_game_duration
                    ?
            start_time
                Unix timestamp of when the match began.
            match_id
                The matches unique ID.
            match_seq_num
                A 'sequence number', representing the order in which matches were recorded.
            tower_status_radiant
                See #Tower Status below.
            tower_status_dire
                See #Tower Status below.
            barracks_status_radiant
                See #Barracks Status below.
            barracks_status_dire
                See #Barracks Status below.
            cluster
                The server cluster the match was played upon. Used for downloading replays of matches. Can be translated to region using dota constants (https://github.com/odota/dotaconstants).
            first_blood_time
                The time in seconds since the match began when first-blood occurred.
            lobby_type
                -1 - Invalid
                0 - Public matchmaking
                1 - Practise
                2 - Tournament
                3 - Tutorial
                4 - Co-op with bots.
                5 - Team match
                6 - Solo Queue
                7 - Ranked
                8 - 1v1 Mid
            human_players
                The amount of human players within the match.
            leagueid
                The league that this match was a part of. A list of league IDs can be found via the GetLeagueListing method.
            positive_votes
                The number of thumbs-up the game has received by users.
            negative_votes
                The number of thumbs-down the game has received by users.
            game_mode
                0 - None
                1 - All Pick
                2 - Captain's Mode
                3 - Random Draft
                4 - Single Draft
                5 - All Random
                6 - Intro
                7 - Diretide
                8 - Reverse Captain's Mode
                9 - The Greeviling
                10 - Tutorial
                11 - Mid Only
                12 - Least Played
                13 - New Player Pool
                14 - Compendium Matchmaking
                15 - Co-op vs Bots
                16 - Captains Draft
                18 - Ability Draft
                20 - All Random Deathmatch
                21 - 1v1 Mid Only
                22 - Ranked Matchmaking
                23 - Turbo Mode
            picks_bans
                A list of the picks and bans in the match, if the game mode is Captains Mode, or bans if not Captains Mode.
            is_pick
                Whether this entry is a pick (true) or a ban (false).
            hero_id
                The hero's unique ID. A list of hero IDs can be found via the GetHeroes method.
            team
                The team who chose the pick or ban; 0 for Radiant, 1 for Dire.
            order
                The order of which the picks and bans were selected; 0-19.
            flags
                ?
            engine
                0 - Source 1
                1 - Source 2
            radiant_score
                Radiant kills
            dire_score
                Dire kills

        """
        r = requests.get(
            "http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1?key={}&match_id={}".format(
                self.STEAM_API_KEY,
                match_id))

        if r.status_code != 200:
            r.raise_for_status()

        return r.json()["result"]

    def get_match_history(self, hero_id: int = None, game_mode: int = None, skill: int = None, min_players: int = None,
                          account_id: str = None, league_id: str = None, start_at_match_id: str = 5806455386,
                          matches_requested: str = "500", tournament_games_only: str = None):
        """
        A list of matches, filterable by various parameters.

        :param hero_id: A list of hero IDs can be found via the GetHeroes method.
        :param game_mode:
            0 - None,
            1 - All Pick
            2 - Captain's Mode
            3 - Random Draft
            4 - Single Draft
            5 - All Random
            6 - Intro
            7 - Diretide
            8 - Reverse Captain's Mode
            9 - The Greeviling
            10 - Tutorial
            11 - Mid Only
            12 - Least Played
            13 - New Player Pool
            14 - Compendium Matchmaking
            16 - Captain's Draft
        :param skill: Skill bracket for the matches (Ignored if an account ID is specified). 0 Any, 1 Normal, 2 High, 3 Very High
        :param min_players: Minimum amount of players in a match for the match to be returned.
        :param account_id: 32-bit account ID.
        :param league_id: Only return matches from this league. A list of league IDs can be found via the GetLeagueListing method.
        :param start_at_match_id: Start searching for matches equal to or older than this match ID.
        :param matches_requested: Amount of matches to include in results (default: 25).
        :param tournament_games_only: Whether to limit results to tournament matches. (0 = false, 1 = true)
        :return:

        result
            status
                1 - Success
                15 - Cannot get match history for a user that hasn't allowed it.
            statusDetail
                A message explaining the status, should status not be 1.
            num_results
                The number of matches in this response.
            total_results
                The total number of matches for the query.
            results_remaining
                The number of matches left for this query.
            matches
                A list of matches.

                match_id
                    The matches unique ID.
                match_seq_num
                    A 'sequence number', representing the order in which matches were recorded.
                start_time
                    Unix timestamp of when the match began.
                lobby_type
                    -1 - Invalid
                    0 - Public matchmaking
                    1 - Practise
                    2 - Tournament
                    3 - Tutorial
                    4 - Co-op with bots.
                    5 - Team match
                    6 - Solo Queue
                    7 - Ranked Matchmaking
                    8 - 1v1 Solo Mid
                players
                    The list of players within the match.
                account_id
                    32-bit account ID.
                player_slot
                    See #Player Slot below.
                hero_id
                    The hero's unique ID. A list of hero IDs can be found via the GetHeroes method.
        """

        base_url = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1?key={}".format(STEAM_API_KEY)
        params = extract_params(locals())

        # construct url
        url = "".join([base_url, params])

        r = requests.get(url)

        if r.status_code != 200:
            r.raise_for_status()

        # only return match_ids
        match_ids = [{
            "match_id": x["match_id"],
            "players": x["players"]} for x in r.json()["result"]["matches"]]
        return match_ids

    def get_match_history_by_sequence_num(self, start_at_match_seq_num: int = None, matches_requested: int = None):
        """
        A list of matches ordered by their sequence num.

        :param start_at_match_seq_num: The match sequence number to start returning results from.
        :param matches_requested: The amount of matches to return.
        :return:
        result
            status
                1 - Success
                8 - 'matches_requested' must be greater than 0.
            statusDetail
                A message explaining the status, should status not be 1.
            matches
                A list of matches.
                See WebAPI/GetMatchDetails the structure of each match.
        """
        base_url = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/v1?key={}".format(
            self.STEAM_API_KEY)
        params = extract_params(locals())

        url = "".join([base_url, params])

        r = requests.get(url)
        if r.status_code != 200:
            r.raise_for_status()

        return r.json()["result"]


if __name__ == '__main__':
    load_dotenv()
    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    api_scraper = Scraper(STEAM_API_KEY)

    pprint(api_scraper.get_match_history(game_mode=1, skill=3, min_players=10))

