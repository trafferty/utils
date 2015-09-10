#!/usr/bin/env python


import json
import sys
import argparse
import datetime
import time
import os
import random

def parse_json_log(json_logoutput_path, start_date='', end_date=''):


    f = open(processLog, 'r')

    #
    # Use start_date and (possibly) end_date to limit the amount
    # of the log that we parse
    #
    start_offset = 0
    if start_date:
        match = re.search(start_date, f.read())
        if match:
            start_offset = match.span()[0]
            print "Startdate found...seeking to byte offset %d" % (start_offset)
        else:
            print "!! Startdate NOT found...reading from beginning of log"

    end_offset = 0
    if end_date:
        f.seek(0)
        match = re.search(end_date, f.read())
        if match:
            end_offset = match.span()[0]
            if end_offset > start_offset:
                print "End date found...truncating at byte offset %d" % (end_offset)
            else:
                print "End date found, but its before start date.  No truncating..."
                end_offset = 0
        else:
            print "!! End date NOT found...reading to end of log"
            end_offset = 0

    f.seek(start_offset)
    if end_offset > start_offset:
        buf = f.read(end_offset - start_offset)
    else:
        buf = f.read()
    f.close()
    print "start_offset = %d, end_offset = %d, length of buf: %d" % (start_offset, end_offset, len(buf))


f = open('/Users/traff_ss/tmp/briggo/JSON_data.log', 'r')

lines = f.readlines()

for line in lines:
    if '"type": "order"' in line:
        order = json.loads(line)
        drink = order['order']['drinks'][0]
        fname = '/Users/traff_ss/tmp/briggo/drink_%d.json' % (drink['id'])
        f = open(fname, 'w')
        json.dump(drink, f)
        f.close()



import json
f = file.open('/Users/traff_ss/tmp/briggo/JSON_data.log', 'r')
f = open('/Users/traff_ss/tmp/briggo/JSON_data.log', 'r')
l = f.readlines()
len(l)
d=json.loads(l[0])
d
d['type']
d['order']['drinks'][0]
dd = d['order']['drinks'][0]
dd['id']
json.dump(dd, open('/Users/traff_ss/tmp/briggo/drink_29587.json', 'w'))

    now = datetime.datetime.today()
    try:
        blank_str = open(blank_order_file).read()
    except:
        sys.stderr.write("Could not open blank (template) order file: %s\n" % (blank_order_file))
        sys.exit(1)
    new_order = json.loads(blank_str[:-1])

    drinks = json.loads(open(drinks_file).read())
    if "start_id" in drinks:
        drink_list = drinks['drink_list']
        #start_id = drinks['start_id']
        start_id = 96000000 + int(random.random() * 9999)
        location_name = drinks['location_name']
        queue_name = drinks['queue_name']
    else:
        # this is a single drink file
        drink_list = []
        drink_list.append(drinks_file)
        start_id = 96000000 + int(random.random() * 9999)
        location_name = "Braker Lab"
        queue_name = "Tester"

    drinkID_list = []
    for idx, drink_name in enumerate(drink_list):
        print 'adding ' + drink_name
        drink = json.loads(open(drink_name).read())
        drink['id'] = start_id + idx
        drinkID_list.append(start_id + idx)
        drink['date_time'] = now.strftime(date_format)
        drink['receipt']['location_name'] = location_name
        drink['receipt']['name'] = "(%d) %s" % (idx+1, os.path.splitext(drink_name)[0])
        drink['receipt']['order_time'] = now.strftime(date_format)
        drink['receipt']['queue_name'] = "%s %d" % (queue_name, idx+1)
        if "need_lid" not in drink:
            drink['need_lid'] = need_lid
        new_order['order']['drinks'].append(drink)

    new_order['order']['id'] = int(time.time())
    new_order['AutoGen'] = True
    order_str = json.dumps(new_order)
    order_str += EOT
    try:
        f = open(order_file, 'w+')
        f.write(order_str)
        f.close()
    except:
        sys.stderr.write("Could not write order file: %s\n" % (order_file))
        sys.exit(1)
    print "\nCreated order file: %s...contains drinkIDs:" % (order_file)
    print " %s" % (', '.join(str(drinkID) for drinkID in drinkID_list))
    # now create an individual present JSON file for each drink in the order
    print "\nNow creating present files for each drink:"
    build_present_order(', '.join(str(drinkID) for drinkID in drinkID_list), order_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse out individual drink files from an MC-produced JSON drink log')
    parser.add_argument('-j', '--json_log_file', type=str, default="", help='log file with JSON drinks in it')
    parser.add_argument('-s', '--start_date', dest='start_date', type=str,
                        help='(optional) date to start parsing in the form of mm/dd/yyyy', default='')
    args = parser.parse_args()

    if len(args.drinks_file):
        build_drink_order(args.drinks_file, args.order_file, args.need_lid)
    elif len(args.present_drink_ids):
        build_present_order(args.present_drink_ids, args.order_file)
    else:  
        print "Must specify file name for drinks"
