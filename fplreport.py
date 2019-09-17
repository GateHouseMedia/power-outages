# coding: utf-8
import requests

import config
import fpljsoner

import time
import datetime
import simplejson as json
import sqlite3

# Execute on first run only
# c.execute('''drop table master;''')
# c.execute('''CREATE TABLE master (lastupdated text, countyname text, outages integer, restored integer, affected integer, accounts integer, outpct integer);''')

pageurl = "https://www.fplmaps.com/data/storm-outages.js"

source = "storm-outages"

r = requests.get(pageurl)

old = r.content
new = r.content
counter = 0

while counter < 50 and old == new:
    counter += 1
    time.sleep(60)
    r = requests.get(pageurl)
    new = r.content
    # print("Running cycle " + str(counter) + " with old " + old + " and new " + new)

if old != new or not InProduction:
    print("Beginning comparison")
    textpre = str(r.content)
    textpre = textpre[textpre.find("{"):textpre.rfind("}")+1]
    text = json.loads(textpre)
    lastupdated = text['lastupdated']
    results = []
    text["counties"]["statewide"] = text["statewide"]
    text["counties"]["statewide"]["name"] = "Statewide"
    for county in text["counties"]:
        countyname = text["counties"][county]["name"].replace("St Lucie", "St. Lucie").replace("St Johns", "St. Johns")
        outages = text["counties"][county]["numberofoutages"]
        restored = text["counties"][county]["numberofrestored"]
        affected = text["counties"][county]["numberofaffected"]
        accounts = text["counties"][county]["numberofaccounts"]
        outpct = round(100*float(outages)/float(accounts), 1)
        row = (lastupdated, countyname, outages, restored, affected, accounts, outpct, source)
        results.append(row)
    #  c.executemany('INSERT INTO master VALUES (?,?,?,?,?,?,?)', results)
    print("Writing results to database")
    beer = "warm"
    while beer != "cold":
        try:
            conn = sqlite3.connect('fploutages.db')
            c = conn.cursor()
            for row in results:
                c.execute('insert into master values (?,?,?,?,?,?,?,?)', row)
            print("Done writing results to database")
            print("Committing")
            conn.commit()
            beer = "cold"
        except:
            time.sleep(.5)   # Try the database access later

if config.WantJson:
    fpljsoner.jsonme()   # Execute jsoner
