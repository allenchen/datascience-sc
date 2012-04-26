#!/usr/bin/env python

"""
Usage:
  import preprocess
  results = preprocess.process_data()

  Returns a dict of:
    {
      player_id [int]: {
        data: [ [
                  time,
                  p1_wr_against_race2_on_map,
                    p2_wr_against_race1_on_map,
                  p1_wr_on_map,
                    p2_wr_on_map,
                  p1_wr_against_race2_overall,
                    p2_wr_against_race2_overall,
                  p1_wr_against_p2_overall
                ],
                ...
              ],
        targets: [ 0, 1, 1, 0, ... ]  # [self == winner for match]
      }
      :
      :
    }


Cached data:

  { p1_id:
    { 'opp':
      { p2_id: p1_wr_over_p2,
         :
         :
      },

      'map':
      { map_id:
        { 't': p1_wr_over_terran_for_this_map,
          'p': p1_wr_over_protoss_for_this_map,
          'z': p1_wr_over_zerg_for_this_map,
          'r': p1_wr_overall_for_this_map
        }
        :
        :
      },

      'race':
      { 't': p1_wr_over_terran,
        'p': p1_wr_over_protoss,
        'z': p1_wr_over_zerg,
      }
    }
    :
    :
  }

API:

  f(map_id, p1_id, p2_id, time) -> [feature]
    -> { data: [ [feature1], [feature2], ... ], outcomes: [ o1, o2, ... ] }

"""

import pandas
import numpy as np
import math
import datetime
import dateutil.parser
from memoize import memoize
from math import exp
from datetime import date as dt
from pymongo import Connection
import os
from multiprocessing import Pool

try:
  connection = Connection(os.environ['MONGO_SERVER'])
except KeyError:
  connection = Connection()
db = connection['sicp']
# .data table

HEADER_PATH       = 'data/players/header.csv'
RESULTS_PATH      = 'data/players/players.csv'
MAPS_HEADER_PATH  = 'data/maps/header.csv'
MAPS_RESULTS_PATH = 'data/maps/maps.csv'

RACE_MAP = {
  'Protoss': 0,
  'Terran' : 1,
  'Zerg'   : 2
}

def key_for(pid):
  return { 'pid': str(pid) }

def get_record(query):
  """
  Args:
    query [dict, int]
  """
  if type(query) in (int, str):  # pid
    query = key_for(query)

  return db.data.find_one(query)

MIN_DATE = 733981
def normalize_date(d):
  if type(d) == str:
    d = dateutil.parser.parse(d)
  elif type(d) == datetime.datetime:
    pass
  else:
    raise TypeError("argument must be str or datetime.datetime")

  current = datetime.date.today().toordinal()
  tscale = current-MIN_DATE
  normalized = 1.0/(1+np.exp(-(((d.toordinal()-MIN_DATE)/tscale)*12 - 6)))
  return normalized

def get_features(map_id, p1_id, p1_race, p2_id, p2_race, date):
  """
  Prediction for p1's performance against p2 on given map and date

  Args:
    map_id: Map on which the players compete
    p1_id:  First player's id
     p2_id
    p1_race: One of ('t', 'p', 'z')
     p2_race
    date:   String like '2012-04-26' of match date, or a datetime.datetime
  """
  valid_races = [race for race, _ in RACES]
  if p1_race not in valid_races or p2_race not in valid_races:
    raise ValueError("Races must be chosen from {0}".format(valid_races))

  map_id, p1_id, p2_id = [str(x) for x in (map_id, p1_id, p2_id)]
  r1, r2 = get_record(p1_id), get_record(p2_id)

  feature = (
    # time
    normalize_date(date),

    # p1_wr_against_race2_on_map,
    r1['map'][map_id][p2_race],

    #   p2_wr_against_race1_on_map,
    r2['map'][map_id][p1_race],

    # p1_wr_on_map,
    r1['map'][map_id]['rate'],

    #   p2_wr_on_map,
    r2['map'][map_id]['rate'],

    # p1_wr_against_race2_overall,
    r1['race'][p2_race],

    #   p2_wr_against_race2_overall,
    r2['race'][p1_race],

    # p1_wr_against_p2_overall
    r1['opp'][p2_id]
  )

  return feature

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
    earliest = df['date'].min().toordinal()
    current = dt.today().toordinal()
    tscale = current-earliest
    time = [1/(1+exp(-(((d.toordinal()-earliest)/tscale)*12 - 6))) for d in df['date']]
    df['time'] = np.array(time).astype(np.float)
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
    #print "no matches -> 0.5"
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
    #print "w_r_p: no matches (pid: {0}, oid: {1}) -> 0.5".format(player_id, opp_id)
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
    #print "w_r_r_m: no matches -> 0.5"
    return 0.5

  r = float(len(win_df)) / float(n_matches)
  return r

def get_features(time, map_id, pid, prace, oid, orace):
  results_df = load_data([RESULTS_PATH], header_path=HEADER_PATH)
  map_df = load_data([MAPS_RESULTS_PATH], header_path=MAPS_HEADER_PATH)
  df = pandas.merge(results_df, map_df, on='map_id', how='inner')

  # Filter out based on map numbers that are unknown
  df = df[df['map_id'] != 0]
  df = df[df['map_id'] != 222]

  df['winner_race'] = [RACE_MAP[race] for race in df['winner_race']]
  df['loser_race'] = [RACE_MAP[race] for race in df['loser_race']]

  my_win_rate = win_rate_race_map(df, pid, orace, map_id) 
  opp_win_rate = win_rate_race_map(df, oid, prace, map_id)

  # Below for time stuff
  earliest = 733981
  current = dt.today().toordinal()
  tscale = current-earliest
  time = 1/(1+exp(-(((time-earliest)/tscale)*12 - 6)))

  features = np.array([[time,
                        my_win_rate,
                        opp_win_rate,
                        win_rate_map(df, pid, map_id),
                        win_rate_map(df, oid, map_id),
                        win_rate_race(df, pid, orace),
                        win_rate_race(df, oid, prace),
                        win_rate_player(df, pid, oid),#]]).astype(np.float)
                        win_rate_player_map(df, pid, oid, map_id)]]).astype(np.float)
  return features

RACES = ( ('t', RACE_MAP['Terran']),
          ('p', RACE_MAP['Protoss']),
          ('z', RACE_MAP['Zerg']) )
def __persist_datum__(args):
  i, pid, df, player_ids, map_ids, replace_existing = args
  n_pids = len(player_ids)
  d_i = n_pids // 10

  if i % d_i == 0:
    print "{0}%".format(float(i)/n_pids)

  if not replace_existing and db.data.find_one({ 'pid': str(pid) }):
    print "({0} / {1}): {2}".format(i, n_pids, pid)
    return

  datum = {
    'pid': str(pid),
    'opp': {},
    'map': {},
    'race': {}
  }

  # race
  for race_label, race_id in RACES:
    datum['race'][race_label] = win_rate_race(df, pid, race_id)

  # map
  for map_id in map_ids:
    h = {}
    for race_label, race_id in RACES:
      h[race_label] = win_rate_race_map(df, pid, race_id, map_id)
    h['rate'] = win_rate_map(df, pid, map_id)
    datum['map'][str(map_id)] = h

  # opponents
  for opp_id in player_ids:
    if pid == opp_id: continue
    datum['opp'][str(opp_id)] = win_rate_player(df, pid, opp_id)

  if replace_existing:
    db.data.remove({ 'pid': str(pid) })
  db.data.insert(datum)

  #print db.data.find_one({ 'pid': str(pid) })
  print "{0} / {1}: {2}".format(i, n_pids, pid)

def persist_data(df=None, replace_existing=False):
  print "persist_data()"

  if df is None:
    df = pp_df()

  player_ids = list(set(df['winner_id']).union(set(df['loser_id'])))
  map_ids = set(df['map_id'])

  pool = Pool(16)
  pool.map(__persist_datum__, [(i, pid, df, player_ids, map_ids, replace_existing) for i, pid in enumerate(player_ids)])

  print ">>> persist_data() done"

@memoize
def pp_df():
  print "Loading df..."
  results_df = load_data([RESULTS_PATH], header_path=HEADER_PATH)
  map_df = load_data([MAPS_RESULTS_PATH], header_path=MAPS_HEADER_PATH)
  df = pandas.merge(results_df, map_df, on='map_id', how='inner')

  # Filter out based on map numbers that are unknown
  print "Preprocessing df..."
  df = df[df['map_id'] != 0]
  df = df[df['map_id'] != 222]

  df['winner_race'] = [RACE_MAP[race] for race in df['winner_race']]
  df['loser_race'] = [RACE_MAP[race] for race in df['loser_race']]

  for col in ('winner_id', 'loser_id', 'map_id'):
    df[col] = [int(x) for x in df[col]]

  print "pp_df: done"

  return df

@memoize
def process_data():
  """
  win rate: of this player against opponent's race on this map
            if never played on this map, default to 0.5
  """
  df = pp_df()
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

      #my_win_rate, opp_win_rate = win_rate_race_map(df, my_id, opp_race, map_id), win_rate_race_map(df, opp_id, my_race, map_id)

      #r2
      features = np.array([time,
                           win_rate_race_map(df, my_id, opp_race, map_id),
                           win_rate_race_map(df, opp_id, my_race, map_id),
                           win_rate_map(df, my_id, map_id),
                           win_rate_map(df, opp_id, map_id),
                           win_rate_race(df, my_id, opp_race),
                           win_rate_race(df, opp_id, my_race),
                           win_rate_player(df, my_id, opp_id),
                           win_rate_player_map(df, my_id, opp_id, map_id)]).astype(np.float)
      """
      #r1_1
      features = np.array([time,
                           win_rate_map(df, my_id, map_id),
                           win_rate_map(df, opp_id, map_id),
                           win_rate_race(df, my_id, opp_race),
                           win_rate_race(df, opp_id, my_race),
                           win_rate_player(df, my_id, opp_id)]).astype(np.float)

      #r1
      features = np.array([time,
                           my_win_rate,
                           opp_win_rate,
                           win_rate_map(df, my_id, map_id),
                           win_rate_map(df, opp_id, map_id),
                           win_rate_race(df, my_id, opp_race),
                           win_rate_race(df, opp_id, my_race),
                           win_rate_player(df, my_id, opp_id)]).astype(np.float)

      #r0
      features = np.array([time,
                           my_win_rate,
                           opp_win_rate,
                           win_rate_player(df, my_id, opp_id)]).astype(np.float)
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
  persist_data()
  #process_data()
