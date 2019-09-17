#!/usr/bin/env python3
# coding: utf-8

import requests
import simplejson as json

import dukejsoner as jsoner
import config

import base64
from collections import OrderedDict
import sqlite3
import datetime

configurl = "https://outagemap.duke-energy.com/config/config.prod.json"
baseurl = "https://cust-api.duke-energy.com/outage-maps/v1/counties?jurisdiction="
databasefile = 'dukeoutages.db'
jurisdictionswanted = [
    "DEF",   # Duke Energy Florida
    "DEC",   # Duke Energy Carolinas
    "DEI",   # Duke Energy Indiana
    "DEM"    # Duke Energy Ohio and Kentucky, which somehow have an M in them.
]


r = requests.get(configurl)
configjson = json.loads(r.content)
# So the auth string we need for the countyurl is a base64 concatentation of two JSON values separated by a colon,
# prefixed by "Basic "
# For this, Thomas Wilburn is owed many frosty beverages

authstring = bytes("Basic ", "utf-8") + base64.b64encode(bytes(f"{configjson['consumer_key_emp']}:{configjson['consumer_secret_emp']}", 'utf-8'))

cookies = r.cookies

headers = {
    'Accept': 'application/json, text/plain, */*',
    # 'Authorization': 'Basic WVFKRjNFemZsMTAzYUpPZ0NIY3E2ajZmSWYwRW9TRWg6YXFuejNDNDg1VEVXOVB0cQ==',
    'Origin': 'https://outagemap.duke-energy.com',
    'Referer': 'https://outagemap.duke-energy.com/',
    'Sec-Fetch-Mode': 'cors',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}

headers['Authorization'] = authstring

masterdict = OrderedDict()
for jurisdiction in jurisdictionswanted:
    r = requests.get(f"{baseurl}{jurisdiction}", headers=headers, cookies=cookies)
    juridata = json.loads(r.content)
    for nugget in juridata['data']:
        line = OrderedDict()
        state = nugget['state']
        countyname = nugget['countyName']
        accounts = nugget['customersServed']
        outages = nugget['areaOfInterestSummary']['maxCustomersAffected']
        if outages is None:
            outages = 0
        line['accounts'] = accounts
        line['outages'] = outages
        if state not in masterdict:
            masterdict[state] = OrderedDict()
        if countyname != "General office":
            masterdict[state][countyname] = line

for state in masterdict:
    totalaccounts = 0
    totaloutages = 0
    for county in masterdict[state]:
        totalaccounts += masterdict[state][county]['accounts']
        totaloutages += masterdict[state][county]['outages']
    line = OrderedDict()
    line['accounts'] = totalaccounts
    line['outages'] = totaloutages
    masterdict[state]['Statewide'] = line

for state in masterdict:
    for county in masterdict[state]:
        masterdict[state][county]['outpct'] = round(100*float(masterdict[state][county]['outages'])/float(masterdict[state][county]['accounts']), 1)


# lastupdated text, state text, countyname text, outages integer, accounts integer, outpct real
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
results = []
for state in masterdict:
    for county in masterdict[state]:
        line = [timestamp, state, county]
        for entry in ["outages", "accounts", "outpct"]:
            line.append(masterdict[state][county][entry])
        results.append(line)

conn = sqlite3.connect(databasefile)
c = conn.cursor()

# Execute on first run only
# c.execute('''drop table master;''')
# c.execute('''CREATE TABLE master (lastupdated text, state text, countyname text, outages integer, accounts integer, outpct real);''')
# conn.commit()

for row in results:
    c.execute('insert into master values (?,?,?,?,?,?)', row)
conn.commit()

if config.WantJson:
    jsoner.jsonme()   # Execute jsoner
