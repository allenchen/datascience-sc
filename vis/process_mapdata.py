import csv
import collections
import sys
from pandas import *
import numpy as np

zcta_to_fips = {}
fips_mi = {}
fips_pop = {}
donations = {
    "Republican": collections.defaultdict(float),
    "Democrat": collections.defaultdict(float),
    "Libertarian": collections.defaultdict(float),
}

def add_party_column(df):
    party_map = {'P20002556': 0, 'P20003109': 0, 'P20002978': 0, 'P20002671': 2, 'P60003654': 0, 'P20002721': 0, 'P20003067': 0, 'P80003353': 0, 'P00003608': 0, 'P20003281': 0, 'P80000748': 0, 'P20002523': 0, 'P80003338': 1}
    party_names = { 0: "Republican", 1: "Democrat", 2: "Libertarian" }
    df.insert(len(df.columns), "party", '')
    
    # cache the id column
    candidate_ids = df['cand_id']

    for i in xrange(len(df)):
        df['party'][i] = party_names[party_map[candidate_ids[i]]]

#print "Processing ZCTA Data"
# Open ZIP Code to FIPS dataset
# from http://mcdc2.missouri.edu/pub/data/georef/zcta_master.Metadata.html
# http://mcdc2.missouri.edu/pub/data/georef/zcta_master.csv
zcta_data = csv.reader(open("zcta_master.csv", "r"))
zcta_data.next()
zcta_data.next()
for row in zcta_data:
    zcta_to_fips[row[1]] = row[2]

#print "Processing Median Income Data"
# Open Median Income per county data
# from US Census
# it's in a really stupid excel CSV format since the data is actually an .xls -_-
# http://www.census.gov/did/www/saipe/data/statecounty/data/2010.html
mi_data = csv.reader(open("median_income_data.csv", "rU"))
mi_data.next()
for row in mi_data:
    fips_mi[str(row[0] + row[1])] = int(row[22].replace(',', '')) if row[22] else 0

#print "Processing Population Data"
# Open Population data
# from US Census
# http://www.census.gov/geo/www/2010census/centerpop2010/county/countycenters.html
pop_data = csv.reader(open("population_data.csv", "r"))
pop_data.next()
for row in pop_data:
    fips_pop[str(row[0] + row[1])] = int(row[4])

#print "Processing Donation Data + Adding Party"
df = read_csv('P00000001-ALL.txt')
add_party_column(df)

for i,party in enumerate(df['party']):
    if str(df['contbr_zip'][i])[:5] in zcta_to_fips:
        donations[party][zcta_to_fips[df['contbr_zip'][i][:5]]] += \
            float(df['contb_receipt_amt'][i])

#print "Processing Division by Population"
for k in donations:
    for fips in donations[k]:
        if (fips not in fips_pop):
            # No census data for this; ignore (we don't color it at all)
            donations[k][fips] = -1
        else:
            donations[k][fips] = donations[k][fips] / fips_pop[fips]

diff_donations = {}

for fips in donations["Republican"]:
    if (fips not in fips_pop):
        diff_donations[fips] = -1
    else:
        # the red/blue color works like this: lower values are colored red, and
        # higher values are colored blue.  we add the mean of democrat donation to 
        # make the average coloring the border between blue and red
        diff_donations[fips] = max(0, donations["Democrat"][fips] - donations["Republican"][fips]) + 1.41

# output to .csv file
# python prints dictionaries in almost-json format (need to replace ' with ") 
print diff_donations
