import simplejson as json

import config

import sqlite3
import datetime

from time import sleep


def jsonme():
    databasefile = 'fploutages.db'
    shortname = "fpl"
    jsonpath = config.jsonpath
    earliestdate = config.earliestdate

    # Naming convention:
    # Short statename-city or region
    # Use "statewide" for statewide results
    # Use a city name when more than one county is involved
    # Use just county name when one county is involved.

    zones = {
        "fl-statewide": '("Statewide")',
        "fl-palmbeach": '("Palm Beach")',
        "fl-daytona": '("Volusia", "Flagler")'   # Danger!
    }

    # Most of the time, FPL spits out outages in one particular file URL and schema (see fplreport2.py).
    # In parts of major disasters, FPL spits out outages in the other format (see fplreport.py).
    # countyoutages is from the regular stuff in No. 2.
    # storm-outages is the major emergency stuff from scraper No. 1.
    # "Look out for No. 1 and try not to step in No. 2." -- Rodney Dangerfield

    source = "countyoutages"   # Regular stuff
    # source = "storm-outages"   # OMG hurricane stuff.

    beer = "warm"
    while beer != "cold":
        try:
            masterdict = {}
            conn = sqlite3.connect(databasefile)
            cursor = conn.cursor()
            for zone in zones:
                querytext = f"SELECT lastupdated, outpct, sum(outages) as 'outages', sum(accounts) as 'accounts' "
                querytext += "from master "
                # querytext += "where substr(lastupdated, 2)='09' "
                # querytext += f"and countyname='{zones[zone]}' "
                querytext += f"where countyname in {zones[zone]} "
                querytext += f"and source='{source}' "
                querytext += "group by lastupdated;"
                cursor.execute(querytext)
                masterdict[zone] = []
                rows = cursor.fetchall()
                for row in rows:
                    d = {}
                    mydatetime = datetime.datetime.strptime(row[0], "%m/%d/%Y %I:%M %p")
                    d['lastupdated'] = datetime.datetime.strftime(mydatetime, "%a %I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.").replace(" 0", " ")
                    d['outpct'] = row[1]
                    d['accounts'] = row[3]
                    d['outpctgood'] = round(100*float(row[2])/float(row[3]), 2)
                    d['outages'] = row[2]
                    d['sortabletime'] = mydatetime.strftime("%Y%m%d-%H%M")
                    if mydatetime >= earliestdate:
                        masterdict[zone].append(d)
            beer = "cold"  # If successfully passed
        except:
            sleep(7)   # Wait to try database again

    for zone in zones:
        newlist = sorted(masterdict[zone], key=lambda k: k['sortabletime'])
        masterdict[zone] = newlist

    unwanteditems = ["outpct", "sortabletime"]

    for zone in zones:
        for i, row in enumerate(masterdict[zone]):
            for unwanteditem in unwanteditems:
                if unwanteditem in row:
                    del masterdict[zone][i][unwanteditem]

    for zone in zones:
        with open(f"{jsonpath}{zone}-{shortname}.json", "w") as f:
            f.write(json.dumps(masterdict[zone]))


if __name__ == '__main__':
    # jsoner executed as script
    jsonme()
