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
#                 map_size_x, map_size_y, nStartPos,
                 win_rate_against_opponent,
                 win_rate_against_opponent_on_map,
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


HEADER_PATH       = 'data/players/header.csv'
RESULTS_PATH      = 'data/players/players.csv'
MAPS_HEADER_PATH  = 'data/maps/header.csv'
MAPS_RESULTS_PATH = 'data/maps/maps.csv'

RACE_MAP = {
  'Protoss': 0,
  'Terran' : 1,
  'Zerg'   : 2
}

def isnan(x):
  return type(x) == float and math.isnan(x)

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
    earliest = df['date'].min().toordinal() + 0.1   # offset to not get zeros
    df['time'] = np.exp([earliest-d.toordinal() for d in df['date']])

  return df

global __avg_map_size
__avg_map_size = None
def avg_map_size(df):
  global __avg_map_size
  if __avg_map_size is not None:
    return __avg_map_size

  dims = [ map_size.split('x') for map_size in df['map_size'] if not isnan(map_size) ]
  avg_size = (np.average([int(x) for x,y in dims]), np.average([int(y) for x,y in dims]))
  print "Avg size =", avg_size
  __avg_map_size = avg_size
  return avg_size

def win_rate_generic(df, win_df, loss_df):
  n_matches = len(win_df) + len(loss_df)

  if n_matches == 0:
    print "no matches -> 0.5"
    return 0.5

  return float(len(win_df)) / float(n_matches)

@memoize
def win_rate_map(df, player_id, map_id):
  d = df[df['map_id'] == map_id]
  win_df, loss_df = [ d[d[player_col] == player_id] for player_col in ('winner_id', 'loser_id') ]
  return win_rate_generic(df, win_df, loss_df)

@memoize
def win_rate_race(df, player_id, opp_race):
  win_df, loss_df = [df[np.logical_and(df[player_col] == player_id, df[race_col] == opp_race)] for player_col, race_col in ( ('winner_id','loser_race'), ('loser_id','winner_race') )]
  return win_rate_generic(df, win_df, loss_df)

@memoize
def win_rate_player(df, player_id, opp_id):
  win_df, loss_df = [ df[np.logical_and(df[player_col] == player_id, df[opp_col] == opp_id)] for player_col, opp_col in ( ('winner_id', 'loser_id'), ('loser_id', 'winner_id') ) ]

  n_matches = len(win_df) + len(loss_df)

  if n_matches == 0:
    print "w_r_p: no matches -> 0.5"
    return 0.5

  return float(len(win_df)) / float(n_matches)

@memoize
def win_rate_player_map(df, player_id, opp_id, map_id):
  d = df[df['map_id'] == map_id]
  win_df, loss_df = [ d[np.logical_and(d[player_col] == player_id, d[opp_col] == opp_id)] for player_col, opp_col in ( ('winner_id','loser_id'), ('loser_id','winner_id') ) ]

  n_matches = len(win_df) + len(loss_df)

  if n_matches == 0:
    print "w_r_p_m: no matches -> 0.5"
    return 0.5

  r = float(len(win_df)) / float(n_matches)
  return r

@memoize
def win_rate_race_map(df, player_id, opp_race, map_id):
  d = df[df['map_id'] == map_id]
  win_df, loss_df = [ d[np.logical_and(d[player_col] == player_id, d[race_col] == opp_race)] for player_col, race_col in ( ('winner_id','loser_race'), ('loser_id','winner_race') ) ]

  n_matches = len(win_df) + len(loss_df)

  if n_matches == 0:
    print "w_r_r_m: no matches -> 0.5"
    return 0.5

  r = float(len(win_df)) / float(n_matches)
  return r

def process_data():
  """
  win rate: of this player against opponent's race on this map
            if never played on this map, default to 0.5
  """
  results_df = load_data([RESULTS_PATH], header_path=HEADER_PATH)
  map_df = load_data([MAPS_RESULTS_PATH], header_path=MAPS_HEADER_PATH)
  df = pandas.merge(results_df, map_df, on='map_id', how='inner')

  # Filter out based on map numbers that are unknown
  df = df[df['map_id'] != 0]
  df = df[df['map_id'] != 222]

  df['winner_race'] = [RACE_MAP[race] for race in df['winner_race']]
  df['loser_race'] = [RACE_MAP[race] for race in df['loser_race']]

  print df
  print df.head()

  data = {}

  n_rows = len(df)
  PROGRESS_PCT = 10
  d_r = n_rows // PROGRESS_PCT

  for (i_row, row) in df.iterrows():
    map_id, map_size, n_start_pos = [row[k] for k in ('map_id', 'map_size', 'map_spots')]

#    if isnan(map_size):
#      map_size_x, map_size_y = avg_map_size(df)
#    else:
#      map_size_x, map_size_y = (map_size.split('x') if type(map_size) == str else (0, 0))

#    if not isnan(n_start_pos):
#      n_start_pos = len(n_start_pos.split(","))
    time = row['time']

    for win_status, my_str, opp_str in ( (1, 'winner', 'loser'), (0, 'loser', 'winner') ):
      my_id,  my_race  = [row["%s_%s" % (my_str, k)]  for k in ('id', 'race')]
      opp_id, opp_race = [row["%s_%s" % (opp_str, k)] for k in ('id', 'race')]

      my_id, opp_id = int(my_id), int(opp_id)

      if my_id not in data:
        data[my_id] = { 'data': [], 'targets': [] }

      my_win_rate, opp_win_rate = win_rate_race_map(df, my_id, opp_race, map_id), win_rate_race_map(df, opp_id, my_race, map_id)

      features = np.array([time,
                           my_win_rate,
                           opp_win_rate,
                           win_rate_map(df, my_id, map_id),
                           win_rate_map(df, opp_id, map_id),
                           win_rate_race(df, my_id, opp_race),
                           win_rate_race(df, opp_id, my_race),
                           win_rate_player(df, my_id, opp_id)]).astype(np.float)
      #win_rate_player_map(df, my_id, opp_id, map_id)
                           
      """
      features = np.array([my_win_rate,
                           win_rate_player(df, my_id, opp_id),
                           win_rate_player_map(df, my_id, opp_id, map_id),
                           win_rate_map(df, my_id, map_id),
                           win_rate_race(df, my_id, opp_race),
                           opp_win_rate, time]).astype(np.float)
      """
      """
      features = np.array([my_race, my_win_rate, 
                           win_rate_player(df, my_id, opp_id), 
                           opp_race, opp_win_rate, time]).astype(np.float)
      """

      """
      features = np.array([my_race, opp_race, my_win_rate, opp_win_rate,
        #map_size_x, map_size_y, n_start_pos,
        win_rate_player(df, my_id, opp_id),
        time]).astype(np.float)
      """

      data[my_id]['data'].append(features)
      data[my_id]['targets'].append(win_status)

      if i_row % d_r == 0:
        print "{0}%".format(float(i_row)/float(n_rows))
        print "  ", my_id, ":", data[my_id], "\n"
        #print my_id, ':', data[my_id]

  for player_id in data.iterkeys():
    data[player_id]['data']    = np.array(data[player_id]['data'])
    data[player_id]['targets'] = np.array(data[player_id]['targets']).astype(np.int)

  print data.iteritems().next()
#  print [type(x) for i, x in data.iteritems().next()]

  return data

if __name__ == "__main__":
  process_data()
