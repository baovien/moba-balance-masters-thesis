# https://demodota2api.readthedocs.io/en/latest/
# https://steamwebapi.azurewebsites.net/
# https://github.com/kshahnazari1998/SmartDota-Public/tree/e876bba502ef4ada17e04b5d309020b9c3d6e522/2_Scraper_Scripts
import json
import dota2api
import requests
from dotenv import load_dotenv

load_dotenv()

api = dota2api.Initialise()

r_heroes = requests.get("https://api.opendota.com/api/heroes")
if (r_heroes.ok):
    print("got heroes map")
    heroes = json.loads(r_heroes.content.decode("utf-8"))

print(api.get_match_history())



