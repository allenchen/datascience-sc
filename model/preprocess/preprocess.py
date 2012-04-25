#!/usr/bin/env python

"""
Usage:
  import preprocess
  results = preprocess.process_data()

  Returns a dict of:
    {
      player_id [int]: {
        data: [ [race, opponent_race,
                 win_rate, opp_win_rate,
                 map_size_x, map_size_y, nStartPos,
                 time
                ],
                ...
              ],
        targets: [ 0, 1, 1, 0, ... ]  # [self == winner for match]
      }
      :
      :
    }
"""

import pandas
import numpy as np
import math
import dateutil.parser
from memoize import memoize


HEADER_PATH       = '../../scraper/results/sc2-international/header.csv'
RESULTS_PATH      = '../../scraper/results/sc2-international/results_p200_p1323.csv'
MAPS_HEADER_PATH  = '../../scraper/results/maps/header.csv'
MAPS_RESULTS_PATH = '../../scraper/results/maps/results_maps.csv'

RACE_MAP = {
  'Protoss': 0,
  'Terran' : 1,
  'Zerg'   : 2
}

def load_data(result_paths=[], header_path=None, verbose=True):
  header = (pandas.read_csv(header_path) if header_path else None)

  df = pandas.DataFrame(columns=header)
  for path in result_paths:
    df = df.append(pandas.read_csv(path,
      header=None, names=header, parse_dates=True, verbose=verbose
    ), ignore_index=True)

  if 'date' in df.columns.values:
    df['date'] = [dateutil.parser.parse(date) for date in df['date']]

    # time = e^(-(date-earliest))
    earliest = df['date'].min().toordinal()
    df['time'] = np.exp([earliest-d.toordinal() for d in df['date']])

  return df

@memoize
def win_rate(df, player_id, opp_race, map_id):
  d = df[ df['map_id'] == map_id ]
  dfs = [ d[d[col_name] == player_id] for col_name in ('winner_id', 'loser_id') ]

  if sum([len(d) for d in dfs]) == 0:
    return 0.5

  #dfs = [d[d[race_col] == opp_race] for d, race_col in zip(dfs, ('loser_race', 'winner_race'))]
  outcomes = []
  for d, race_col, outcome in zip(dfs, ('loser_race', 'winner_race'), (1,0)):
    d = d[d[race_col] == opp_race]
    outcomes.extend( len(d) * [outcome] )

  if len(outcomes) == 0:
    return 0.5
  else:
    r = np.average(outcomes)

  if math.isnan(r):
    print "failed outcomes:", outcomes
    raise "WAT"

  return r

def process_data():
  """
  win rate: of this player against opponent's race on this map
            if never played on this map, default to 0.5
  """
  results_df = load_data([RESULTS_PATH], header_path=HEADER_PATH)
  map_df = load_data([MAPS_RESULTS_PATH], header_path=MAPS_HEADER_PATH)
  df = pandas.merge(results_df, map_df, on='map_id', how='left')

  df = df[ [x if type(x) == bool else False for x in df['map_name.y'] != 'Unknown'] ]

  print df
  print df.head()

  data = {}

  for (i_row, row) in df.iterrows():
    map_id, map_size, n_start_pos = [row[k] for k in ('map_id', 'map_size', 'map_spots')]

    map_size_x, map_size_y = (map_size.split('x') if type(map_size) == str else (0, 0))

    if not (type(n_start_pos) == float and math.isnan(n_start_pos)):
      n_start_pos = len(n_start_pos.split(","))
    time = row['time']

    for win_status, my_str, opp_str in ( (1, 'winner', 'loser'), (0, 'loser', 'winner') ):
      my_id,  my_race  = [row["%s_%s" % (my_str, k)]  for k in ('id', 'race')]
      opp_id, opp_race = [row["%s_%s" % (opp_str, k)] for k in ('id', 'race')]

      my_race, opp_race = RACE_MAP[my_race], RACE_MAP[opp_race]
      my_id, opp_id = int(my_id), int(opp_id)

      if my_id not in data:
        data[my_id] = { 'data': [], 'targets': [] }

      my_win_rate, opp_win_rate = win_rate(df, my_id, opp_race, map_id), win_rate(df, opp_id, my_race, map_id)

      features = np.array([my_race, opp_race, my_win_rate, opp_win_rate, map_size_x, map_size_y, n_start_pos, time]).astype(np.float)

      data[my_id]['data'].append(features)
      data[my_id]['targets'].append(win_status)
      #print my_id, ':', data[my_id]

  for player_id in data.iterkeys():
    data[player_id]['data']    = np.array(data[player_id]['data'])
    data[player_id]['targets'] = np.array(data[player_id]['targets']).astype(np.int)

#  print data.iteritems().next()
#  print [type(x) for i, x in data.iteritems().next()]

  return data

if __name__ == "__main__":
  process_data()
