# coding: utf-8
import requests
import simplejson as json

import config
import fpljsoner

import sqlite3
import time
import datetime

databasefile = 'fploutages.db'

# Execute on first run only
# c.execute('''drop table master;''')
# c.execute('''CREATE TABLE master (lastupdated text, countyname text, outages integer, restored integer, affected integer, accounts integer, outpct integer, source text);''')
# alter table master add column source text;

outagesurl = "https://www.fplmaps.com/customer/outage/CountyOutages.json"

timestamp = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
source = "countyoutages"
r = requests.get(outagesurl)
textpre = r.content
text = json.loads(textpre)
counties = text['outages']

results = []
totaloutages = 0
totalaccounts = 0
for county in counties:
    countyname = county['County Name']
    outages = int(county['Customers Out'].replace(",", ""))
    accounts = int(county['Customers Served'].replace(",", ""))
    totaloutages += outages
    totalaccounts += accounts
    #         row = (lastupdated, countyname, outages, restored, affected, accounts, outpct)
    outpct = round(100*float(outages)/float(accounts), 1)
    row = (timestamp, countyname, outages, None, None, accounts, outpct, source)
    results.append(row)
totaloutpct = round(100*float(totaloutages)/float(totalaccounts), 1)
row = (timestamp, "Statewide", totaloutages, None, None, totalaccounts, totaloutpct, source)
results.append(row)

beer = "warm"
while beer != "cold":
    try:
        conn = sqlite3.connect(databasefile)
        c = conn.cursor()
        for row in results:
            c.execute('insert into master values (?,?,?,?,?,?,?,?)', row)
        conn.commit()
        beer = "cold"
    except:
        time.sleep(3)   # Wait for access to the database

if config.WantJson:
    fpljsoner.jsonme()   # Execute jsoner
