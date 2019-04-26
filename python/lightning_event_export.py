import sqlite3
#import pandas as pd
import datetime as dt
import argparse

def exportEvents(path_to_db):
    events = []
    db = sqlite3.connect(path_to_db)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cal_events")

    for row in cursor:
        #print(row)
        events.append ({
          'desc': row[4],
          'start_dt': dt.datetime.fromtimestamp(row[9]/1e6),
          'end_dt': dt.datetime.fromtimestamp(row[10]/1e6) })
    return events

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export events from thunderbird/lightning calendar sqlite3 database and push to gcal')
    parser.add_argument('-d', '--database', type=str, default="", help='path to the lightning database file (local.sqlite)')
    parser.add_argument('-g', '--google_info', type=str, default="", help='path to google info file (.json)')
    args = parser.parse_args()


    path_to_db = '/home/trafferty/.thunderbird/kmummskk.default/calendar-data/local.sqlite'
    events = exportEvents(path_to_db)

    for e in events:
        print("%s : %s - %s" % (e['desc'], 
            # dt.datetime.fromtimestamp(e['start_ts']).strftime('%Y-%m-%d %H:%M:%S'), 
            # dt.datetime.fromtimestamp(e['end_ts']).strftime('%Y-%m-%d %H:%M:%S')))
            e['start_dt'].isoformat(), 
            e['end_dt'].isoformat()))
