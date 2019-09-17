import simplejson as json

import config

import sqlite3
import datetime


def jsonme():
    databasefile = 'dukeoutages.db'
    shortname = "duke"
    jsonpath = config.jsonpath
    earliestdate = config.earliestdate

    # Naming convention:
    # Short statename-city or region
    # Use "statewide" for statewide results
    # Use a city name when more than one county is involved
    # Use just county name when one county is involved.

    zones = {   # Full clause after "where" goes here
        "nc-fayetteville": ' state="NC" and countyname in ("Cumberland", "Harnett", "Hoke", "Robeson", "Sampson", "Bladen") ',
        "nc-wilmington": ' state="NC" and countyname in ("New Hanover", "Brunswick", "Pender") ',
        "nc-newbern": ' state="NC" and countyname in ("Craven", "Jones", "Pamlico") ',
        "nc-statewide": ' state="NC" and countyname="Statewide" ',
        "sc-statewide": ' state="SC" and countyname="Statewide" ',
        "fl-statewide": ' state="FL" and countyname="Statewide" ',
        "fl-daytona": ' state="FL" and countyname in ("Volusia", "Flagler")'   # misleading filename
    }

    masterdict = {}
    conn = sqlite3.connect(databasefile)
    cursor = conn.cursor()
    for zone in zones:
        querytext = f"SELECT lastupdated, outpct, sum(outages) as 'outages', sum(accounts) as 'accounts' "
        querytext += "from master "
        querytext += f"where {zones[zone]} "
        querytext += "group by lastupdated order by lastupdated asc;"
        cursor.execute(querytext)
        masterdict[zone] = []
        rows = cursor.fetchall()
        for row in rows:
            d = {}
            mydatetime = datetime.datetime.strptime(row[0], "%Y%m%d-%H%M")
            d['lastupdated'] = datetime.datetime.strftime(mydatetime, "%a %I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.").replace(" 0", " ")
            d['outpct'] = row[1]
            d['accounts'] = row[3]
            d['outpctgood'] = round(100*float(row[2])/float(row[3]), 2)
            d['outages'] = row[2]
            d['sortabletime'] = row[0]
            if mydatetime >= earliestdate:
                masterdict[zone].append(d)

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
