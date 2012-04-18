import csv
import collections
import sys
import math
import string
from pandas import *
import numpy as np
from fmap import fmap
from wilson_score import *

# Make race data look like how the bubble graph expects it:
# {
#   "name": "graph",
#   "children": 
#     [
#       { "name": "Democrat", 
#         "children" :
#           [
#             { "name": "Barack Obama", "size": 100 }
#           ] 
#       },
#       { "name": "Republican", 
#         "children" :
#           [
#             { "name": "Mitt Romney", "size": 25 },
#             { "name": "Rick Santorum", "size": 25 },
#             { "name": "Newt Gingrich", "size": 25 },
#             { "name": "Ron Paul", "size": 25 }
#           ] 
#       },
#       { "name": "Libertarian", 
#         "children" :
#           [
#             { "name": "RJ Harris", "size": 1 },
#           ] 
#       }
#     ]
# }

#graph["children"][0]["children"]
graph = { 
    "name": "graph", 
    "children": 
    [
        { "name": "Zerg",
          "children" : []
          },
        { "name": "Protoss",
          "children" : []
          },
        { "name": "Terran",
          "children": []
          }
        ]
    }

races = {
    "Zerg": fmap(),
    "Protoss": fmap(),
    "Terran": fmap()
}

losingraces = {
    "Zerg": fmap(),
    "Protoss": fmap(),
    "Terran": fmap()
}


df = read_csv('sc2_korean_p0_p199.csv')

for i,race in enumerate(df['winner_race']):
    races[race][df['winner_name'][i]] += 1
for i,race in enumerate(df['loser_race']):
    losingraces[race][df['loser_name'][i]] += 1

# output to .csv file
# python prints dictionaries in almost-json format (need to replace ' with ") 

# Need to prune these (there are a LOT of races!)
# Take the top 50 of each.

top_count = 50

def scale_frequency(wins,losses):
    # use lower bound of Wilson score confidence interval for a Bernoulli parameter W/L
    return math.exp(10+(10*confidence(wins,losses)))
#math.sqrt(confidence(wins,losses))

for player_name, frequency in \
        races["Zerg"].get_top_n(top_count, emitFrequencies=True):
    graph["children"][0]["children"] += [{ "name": player_name, "size": scale_frequency(frequency, losingraces["Zerg"][player_name]) }]

for player_name, frequency in \
        races["Protoss"].get_top_n(top_count, emitFrequencies=True):
    graph["children"][1]["children"] += [{ "name": player_name, "size": scale_frequency(frequency, losingraces["Protoss"][player_name]) }]

for player_name, frequency in \
        races["Terran"].get_top_n(top_count, emitFrequencies=True):
    graph["children"][2]["children"] += [{ "name": player_name, "size": scale_frequency(frequency, losingraces["Terran"][player_name]) }]

print graph
