# coding: utf-8
import requests
import creds
import time
import datetime
from slackclient import SlackClient
import json
import sqlite3
from tqdm import tqdm
import tweepy

InProduction = True
WantTweets = False
WantShortNotice = True
ReportOutagesOver = 1500   # Slack message when we see PBC-MRT-STL outages over 1500, or 0, or whatever.

notify_list = [
    'CMFRQBGD8',    
# 'G0C6WGATZ',        # breaking
    # "C6ZDMT2FR",        # irmachat
    #    "C6Z7Q9MK8",        # irmamultimedia
    'U0569RD2C'         # Stucka
]

PlacesOfInterest = [
    "Palm Beach",
    "St. Lucie",
    "Martin",
    "Statewide"
    ]


# Execute on first run only
# c.execute('''drop table master;''')
# c.execute('''CREATE TABLE master (lastupdated text, countyname text, outages integer, restored integer, affected integer, accounts integer, outpct integer);''')

# server 104.131.186.249
# What does our server do?

pageurl = "https://www.fplmaps.com/data/storm-outages.js"

source = "storm-outages"

slackapikey = creds.access['slackapikey']
slack_client = SlackClient(slackapikey)


def notify(text):
    for notification in notify_list:
        slack_client.api_call(
                "chat.postMessage",
                channel=notification,
                text=text,
                username="DataTeam",
                icon_emoji=':robot_face:'
                )
    return


def tweet_this(text):
    consumer_token = creds.access['twitter_token']
    consumer_token_secret = creds.access['twitter_token_secret']
    consumer_secret = creds.access['twitter_consumer_secret']
    consumer_key = creds.access['twitter_consumer_key']
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(consumer_token, consumer_token_secret)
        twitter_api = tweepy.API(auth)
        print("Trying to tweet out message: \r\n\t" + text)
        twitter_api.update_status(text)
    except:
        print("Twitter posting failed.")
    return


r = requests.get(pageurl)

placetweets = {}

old = r.content
new = r.content
counter = 0

while counter < 50 and old == new:
    counter += 1
    time.sleep(60)
    r = requests.get(pageurl)
    new = r.content
    print("Running cycle " + str(counter) + " with old " + old + " and new " + new)
    if not InProduction:
        break    # For debugging

if old != new or not InProduction:
    print("Beginning comparison")
    textpre = str(r.content)
    textpre = textpre[textpre.find("{"):textpre.rfind("}")+1]
    text = json.loads(textpre)
    lastupdated = text['lastupdated']
    results = []
    notice = "FPL update: " + lastupdated + "\r\n"
    shortnotice = "FPL update: " + lastupdated + ". "
    localoutages = 0
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
        if countyname in PlacesOfInterest:
            notice += countyname + ": "
            notice += str(outpct) + "% without power, "
            notice += str(outages) + " outages, "
            notice += str(restored) + " restored, "
            notice += str(affected) + " affected, "
            notice += str(accounts) + " accounts\r\n"
            shortnotice += countyname + ": "
            shortnotice += str(outages) + " (" + str(outpct) + "%) out, "
            shortnotice += str(restored) + " restored. "
            if countyname != "Statewide":
                localoutages += outages
        placetweets[countyname] = "FPL update: " + lastupdated + "\r\n" + countyname + ": " + str(outpct) + "% without power, " + str(outages) + " outages, " + str(restored) + " restored\r\nSee http://www.palmbeachpost.com"
    #  c.executemany('INSERT INTO master VALUES (?,?,?,?,?,?,?)', results)
    print("Writing results to database")
    conn = sqlite3.connect('fploutages.db')
    c = conn.cursor()
    for row in tqdm(results):
        c.execute('insert into master values (?,?,?,?,?,?,?,?)', row)
    print("Done writing results to database")
    print("Committing")
    conn.commit()
    print("Printing notice thingy")
    print(notice)
    print(shortnotice)

    if localoutages >= ReportOutagesOver:
        print("Trying to Slack this thing")
        try:
            if WantShortNotice:
                notify(text=shortnotice)
            else:
                notify(text=notice)
        except:
            print("Slack failed")

    if WantTweets:
        print("Trying to tweet Palm Beach")
        tweet_this(placetweets["Palm Beach"])
        now = datetime.datetime.now()
        hour = now.hour + 24   # Make sure we don't have zeros
        if now.minute > 30:   # Window the time, ala Y2K
            hour += 1
        remainder = hour % 3    # Remainder of dividing by 3
        time.sleep(300)
        if remainder == 0:
            tweet_this(placetweets["Statewide"])
        elif remainder == 1:
            tweet_this(placetweets["Martin"])
        elif remainder == 2:
            tweet_this(placetweets["St. Lucie"])

    print("All done?")
