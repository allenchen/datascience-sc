import collections
import sys
import math
import string
from pandas import *
import numpy as np
from matplotlib import pyplot as pp
from pylab import *
import random

donation_records = {
    "Republican": {},
    "Democrat": {},
    "Libertarian": {}
    }

def sample_with_replacement(population, k):
    arr = []
    k = int(k)
    for i in xrange(k):
        arr += [random.choice(population.values)]

    return arr

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

FACTOR = 0.1

republican = df[(df['party'] == "Republican") & (df['contb_receipt_amt'] > 0)]['contb_receipt_amt']

for i,amount in enumerate(sample_with_replacement(republican, FACTOR*size(republican))):
    donation_records["Republican"][str(i)] = amount

democrat = df[(df['party'] == "Democrat") & (df['contb_receipt_amt'] > 0)]['contb_receipt_amt']

for i,amount in enumerate(sample_with_replacement(democrat, FACTOR*size(democrat))):
    donation_records["Democrat"][str(i)] = amount

libertarian = df[(df['party'] == "Libertarian") & (df['contb_receipt_amt'] > 0)]['contb_receipt_amt']

for i,amount in enumerate(sample_with_replacement(libertarian, FACTOR*size(libertarian))):
    donation_records["Libertarian"][str(i)] = amount
    
print donation_records
