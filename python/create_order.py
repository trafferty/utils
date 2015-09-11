#!/usr/bin/env python


import json
import sys
import argparse
import datetime
import time
import os
import random

EOT = '\x04'
blank_order_file = 'order_blank.json'
date_format = "%m/%d/%y %H:%M%p"

def ADC_to_DegreesF(ADC_Value):
    ADC_Value = float(ADC_Value) # make sure this is a float!
    return (25.928*((ADC_Value-30530)/32768*21.164 + 0.992)**1 
    + -0.7602961 * ((ADC_Value-30530)/32768*21.164 + 0.992)**2 
    + 0.04637791*((ADC_Value-30530)/32768*21.164 + 0.992)**3 
    + -0.002165394*((ADC_Value-30530)/32768*21.164 + 0.992)**4 
    + 0.00006048144*((ADC_Value-30530)/32768*21.164 + 0.992)**5 
    + -0.0000007293422*((ADC_Value-30530)/32768*21.164 + 0.992)**6 
    + 0 * ((ADC_Value-30530)/32768*21.164 + 0.992)**7) * 9.0/5.0 + 32

def change_to_degreesF(steps):
    for step in steps:
        if 'temperature' in step:
            if step['temperature'] > 255:
                print "Changing ADC value of %d..." % (step['temperature'])
                step['temperature'] = ADC_to_DegreesF(step['temperature'])
                print "...to %f F" % (step['temperature'])

def build_present_order(present_drink_ids, out_file, auto_present):
    drink_ids = present_drink_ids.split(',')
    for idx, drink_id in enumerate(drink_ids):
        print "Creating present_drink_id(%d): %s" % (idx, drink_id.strip())
        present_cmd = {}
        present_cmd['command'] = 'present'
        present_cmd['type'] = 'command'
        present_cmd['drink_id'] = int(drink_id.strip())
        present_str = json.dumps(present_cmd)
        present_str += EOT
        try:
            out_file_path = os.path.dirname(out_file)
            if auto_present:
                present_file = "%s/present_%s.json" % (out_file_path, drink_id.strip())
            else:
                present_file = "%s/present_%s.jsonX" % (out_file_path, drink_id.strip())
            f = open(present_file, 'w+')
            f.write(present_str)
            f.close()
        except:
            sys.stderr.write("Could not write order file: %s\n" % (present_file))
            sys.exit(1)
        #time.sleep(1.5)

def build_drink_order(drinks_file, order_file, need_lid, degreesF):
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
        drink['receipt']['name'] = "(%d) %s" % (idx+1, os.path.basename(drink_name).split('.')[0])
        drink['receipt']['order_time'] = now.strftime(date_format)
        drink['receipt']['queue_name'] = "%s %d" % (queue_name, idx+1)
        if "need_lid" not in drink:
            drink['need_lid'] = need_lid
        if degreesF:
            change_to_degreesF(drink['steps'])
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
    build_present_order(', '.join(str(drinkID) for drinkID in drinkID_list), order_file, False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build a test order with drinks defined in specified JSON file')
    parser.add_argument('-d', '--drinks_file', type=str, default="", help='JSON file listing the drinks in the order')
    parser.add_argument('-p', '--present_drink_ids', type=str, default="", help='Drink ID of drink you want to present')
    parser.add_argument('-o', '--order_file', type=str, help='Output order file', required=True)
    parser.add_argument('--lids', dest='need_lid', action='store_true')
    parser.add_argument('--no-lids', dest='need_lid', action='store_false')
    parser.add_argument('--degreesF', dest='degreesF', action='store_true')
    parser.set_defaults(need_lid=True)
    parser.set_defaults(degreesF=False)
    args = parser.parse_args()

    if len(args.drinks_file):
        build_drink_order(os.path.abspath(args.drinks_file), os.path.abspath(args.order_file), args.need_lid, args.degreesF)
    elif len(args.present_drink_ids):
        build_present_order(args.present_drink_ids, args.order_file, True)
    else:  
        print "Must specify file name for drinks"
