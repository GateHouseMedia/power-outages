import simplejson as json

import config

import sqlite3
import datetime


def jsonme():
    databasefile = 'ncemcoutages.db'
    shortname = "emc"
    jsonpath = config.jsonpath
    earliestdate = config.earliestdate

    zones = {
        "nc-fayetteville": ' countyname in ("Cumberland", "Harnett", "Hoke", "Robeson", "Sampson", "Bladen") ',
        "nc-wilmington": ' countyname in ("New Hanover", "Brunswick", "Pender") ',
        "nc-newbern": ' countyname in ("Craven", "Jones", "Pamlico") ',
        "nc-statewide": ' countyname="Statewide" '
    }

    masterdict = {}
    conn = sqlite3.connect(databasefile)
    cursor = conn.cursor()
    for zone in zones:
        querytext = f"SELECT lastupdated, sum(outages) as 'outages' "
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
            d['outages'] = row[1]
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
