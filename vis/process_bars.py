import csv
import collections
import sys
import math
import string
from pandas import *
import numpy as np
from fmap import fmap
from datetime import datetime

league_ids = set()

df = read_csv('sc2_korean_p0_p199.csv')

for league_id in df['league_id']:
    league_ids.add(league_id)

ordered_leagues = list(league_ids)
ordered_leagues.sort()

string_party_map = {
    "Zerg" : 0,
    "Protoss" : 1,
    "Terran" : 2
}

date_map = {
    "Zerg": [0]*len(ordered_leagues),
    "Protoss": [0]*len(ordered_leagues),
    "Terran": [0]*len(ordered_leagues)
}

formatted_date_map = {
    "Zerg": [0]*len(ordered_leagues),
    "Protoss": [0]*len(ordered_leagues),
    "Terran": [0]*len(ordered_leagues)
}

for i,race in enumerate(df['winner_race']):
    date_map[race][ordered_leagues.index(df['league_id'][i])] += 1

for pid, party in enumerate(date_map):
    for i,value in enumerate(date_map[party]):
        formatted_date_map[party][i] = { "x": i, "y": value, "p": string_party_map[party] }

print formatted_date_map
