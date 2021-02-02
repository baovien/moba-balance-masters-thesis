import os
import ujson
import requests
from pprint import pprint
from dotenv import load_dotenv


def get_match_ids(tier):
    """
    Get match ids from chosen tier by using datdota.com

    :param tier: semipro/professional/premium
    :return:
    """
    r = requests.get(f"http://datdota.com/api/matches?tier={tier}")

    r.raise_for_status()

    data = r.json()
    latest_matchid = data["data"][0]["matchId"]
    save_path = f"data/matchids/{tier}_{latest_matchid}.json"

    with open(save_path, 'w') as fp:
        ujson.dump(data, fp)

    print("done")


if __name__ == '__main__':
    get_match_ids("premium")
