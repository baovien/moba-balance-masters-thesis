import requests
import json
import csv

api_key = "" # Enter STEAM API key here.

url_heroes = "https://api.opendota.com/api/heroes"
response_heroes = requests.get(url_heroes)
if (response_heroes.ok):
    data_heroes = json.loads(response_heroes.content.decode("utf-8"))
heroes = [''] * 226
for i in range(len(data_heroes)):
    heroes[data_heroes[i]["id"]-1] = data_heroes[i]["localized_name"] + " (radiant)"
for i in range(len(data_heroes)):
    heroes[data_heroes[i]["id"] + len(data_heroes)] = data_heroes[i]["localized_name"] + " (dire)"
heroes.append("Radiant win")

with open('results.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(heroes)