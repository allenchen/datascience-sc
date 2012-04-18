import csv
import collections
import sys
import math
import string
from pandas import *
import numpy as np
from fmap import fmap
from datetime import datetime

candidates = ["Bachmann, Michelle",
"Cain, Herman",
"Gingrich, Newt",
"Huntsman, Jon",
"Johnson, Gary Earl",
"McCotter, Thaddeus G",
"Obama, Barack",
"Paul, Ron",
"Pawlenty, Timothy",
"Perry, Rick",
"Roemer, Charles E. 'Buddy' III",
"Romney, Mitt",
"Santorum, Rick"]

candidate_donations = {}
for c in candidates:
    candidate_donations[c] = 0

republican_total = 0
republicans = 11

party_map = {}

def add_party_column(df):
    party_map = {'P20002556': 0, 'P20003109': 0, 'P20002978': 0, 'P20002671': 2, 'P60003654': 0, 'P20002721': 0, 'P20003067': 0, 'P80003353': 0, 'P00003608': 0, 'P20003281': 0, 'P80000748': 0, 'P20002523': 0, 'P80003338': 1}
    party_names = { 0: "Republican", 1: "Democrat", 2: "Libertarian" }
    df.insert(len(df.columns), "party", '')
    
    # cache the id column
    candidate_ids = df['cand_id']
    
    for i in xrange(len(df)):
        df['party'][i] = party_names[party_map[candidate_ids[i]]]

df = read_csv('P00000001-ALL.txt')
add_party_column(df)

libertarian_total = 0
democrat_total = 0

for candidate in candidates:
    df2 = df[df['cand_nm'] == candidate]
    candidate_donations[candidate] = sum(df2['contb_receipt_amt'])
    if (df2['party'].values[0] == 'Republican'):
        republican_total += candidate_donations[candidate]
    if (df2['party'].values[0] == 'Democrat'):
        democrat_total += candidate_donations[candidate]
    if (df2['party'].values[0] == 'Libertarian'):
        libertarian_total += candidate_donations[candidate]
    party_map[candidate] = df2['party'].values[0]

repub_avg = republican_total/republicans
dem_avg = democrat_total
lib_avg = libertarian_total

arr = []
for k,v in candidate_donations.iteritems():
    item = {"title": k,
            "subtitle": party_map[k],
            "ranges": [int(lib_avg), int(repub_avg), int(dem_avg)],
            "measures": [int(v)],
            "markers": [repub_avg]}
    arr += [item]

print arr
