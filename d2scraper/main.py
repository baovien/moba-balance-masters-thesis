# https://dev.dota2.com/forum/dota-2/spectating/replays/webapi/60177-things-you-should-know-before-starting?t=58317

import os
from dotenv import load_dotenv

load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")


if __name__ == '__main__':
    print(STEAM_API_KEY)

