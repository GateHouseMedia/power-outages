#!/usr/bin/env python
# coding: utf-8

import requests
import simplejson as json
from pyquery import PyQuery as pq

import config
import ncemcjsoner

import datetime
import csv
import sqlite3

hosturl = "https://outages.ncelectriccooperatives.com/outages/maps"
dataurl = "https://outages.ncelectriccooperatives.com/outages/details"
databasefile = 'ncemcoutages.db'

counties = ["Alamance", "Alexander", "Alleghany", "Anson", "Ashe", "Avery", "Beaufort", "Bertie", "Bladen", "Brunswick", "Buncombe", "Burke", "Cabarrus", "Caldwell", "Camden", "Carteret", "Caswell", "Catawba", "Chatham", "Cherokee", "Chowan", "Clay", "Cleveland", "Columbus", "Craven", "Cumberland", "Currituck", "Dare", "Davidson", "Davie", "Duplin", "Durham", "Edgecombe", "Forsyth", "Franklin", "Gaston", "Gates", "Graham", "Granville", "Greene", "Guilford", "Halifax", "Harnett", "Haywood", "Henderson", "Hertford", "Hoke", "Hyde", "Iredell", "Jackson", "Johnston", "Jones", "Lee", "Lenoir", "Lincoln", "McDowell", "Macon", "Madison", "Martin", "Mecklenburg", "Mitchell", "Montgomery", "Moore", "Nash", "New Hanover", "Northampton", "Onslow", "Orange", "Pamlico", "Pasquotank", "Pender", "Perquimans", "Person", "Pitt", "Polk", "Randolph", "Richmond", "Robeson", "Rockingham", "Rowan", "Rutherford", "Sampson", "Scotland", "Stanly", "Stokes", "Surry", "Swain", "Transylvania", "Tyrrell", "Union", "Vance", "Wake", "Warren", "Washington", "Watauga", "Wayne", "Wilkes", "Wilson", "Yadkin", "Yancey"]

timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")

# Below code seemed to be needed for authentication ... except maybe it was always a POST instead of a GET

# r = requests.get(hosturl)
# cookies = r.cookies
# payload = {
    # 'Accept': 'application/json, text/javascript, */*; q=0.01',
    # 'Accept-Encoding': 'gzip, deflate, br',
    # 'Accept-Language': 'en-US,en;q=0.9',
    # 'Connection': 'keep-alive',
    # 'Content-Length': '0',
    # 'Host': 'outages.ncelectriccooperatives.com',
    # 'Origin': 'https://outages.ncelectriccooperatives.com',
    # 'Referer': 'https://outages.ncelectriccooperatives.com/outages/maps',
    # 'Sec-Fetch-Mode': 'cors',
    # 'Sec-Fetch-Site': 'same-origin',
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    # 'X-Requested-With': 'XMLHttpRequest'
# }

# r = requests.post(dataurl, cookies=cookies, data=payload)

r = requests.post(dataurl)

fml = json.loads(r.content)
html = fml['DetailsByCountyAlpha'].replace("\r", "").replace("\n", "").replace("\t", "").replace(" County (NC)", "").replace(" member(s) affected.", "")

totaloutages = 0
masterdict = {}
for county in counties:
    masterdict[county] = 0

for dl in pq(html)("dl"):
    county = pq(dl)("dt").text().strip()
    outages = int(pq(dl)("p").text().strip().replace(",", ""))
    totaloutages += outages
    if county not in masterdict:
        print(f"Found new county: {county}")
    if " County (GA)" not in county and " County (TN)" not in county:
        masterdict[county] = outages
masterdict['Statewide'] = totaloutages

conn = sqlite3.connect(databasefile)
c = conn.cursor()

# Execute on first run only
# c.execute('''CREATE TABLE master (lastupdated text, countyname text, outages integer);''')
# conn.commit()

for county in masterdict:
    row = [timestamp, county, masterdict[county]]
    c.execute('insert into master values (?,?,?)', row)
conn.commit()

if config.WantJson:
    ncemcjsoner.jsonme()   # Execute jsoner
