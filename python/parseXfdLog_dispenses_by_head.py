#!/usr/bin/env python2

import sys
import os
import re
import argparse
import json
import glob
import datetime as dt

def set_default(obj):
    if isinstance(obj, set):
        return sorted(list(obj))
    raise TypeError

def parseXfdLog(xfdLog, results_dict):
    '''
    '''
    with open(xfdLog, 'r') as log_file:
        buf = log_file.read()
    buf = buf.replace('\r\n', '\n') # get rid of windows line endings...
    print("File (%s) opened and read into buffer, length of buf: %d" % (xfdLog, len(buf)))

    serial_num_pattern = ur"\n(?P<date_XFD_started>201.-..-..)\ (?P<time_XFD_started>[0-9:,]*)\ INFO.*?head_head[ABCD]_serial: \"(?P<serial_num>[0-9]*)\"\n"
    dispense_event_pattern = ur"\n(?P<date_dispensed>201.-..-..)\ (?P<time_dispensed>[0-9:,]*)\ INFO .*?Dispensing pattern for tcs:[0-9] recipe:[0-9] swathe:[0-9]\n"

    serial_num_matches = re.finditer(serial_num_pattern, buf, re.MULTILINE)
    dispense_event_matches = re.finditer(dispense_event_pattern, buf, re.MULTILINE)

    serial_num = 'S/N: unknown'
    for match in serial_num_matches:
        serial_num = "S/N: %s" % (match.groupdict()['serial_num'])
        print("XFD started on %s at %s with dispenser serial num: %s..." % (match.groupdict()['date_XFD_started'], match.groupdict()['time_XFD_started'], serial_num))

    print("Starting search for dispenses for serial num: %s" % (serial_num))

    for match in dispense_event_matches:
        year = match.groupdict()['date_dispensed'][0:4]

        if year not in results_dict:
            results_dict[year] = {}
        
        if serial_num not in results_dict[year]:
            results_dict[year][serial_num]={}
            results_dict[year][serial_num]['dispense count'] = 0
            results_dict[year][serial_num]['dispense dates']= set() 

        results_dict[year][serial_num]['dispense count'] += 1
        results_dict[year][serial_num]['dispense dates'].add(match.groupdict()['date_dispensed'])

        if serial_num is 'unknown':
            print( "  Unknown! Dispensed on %s at %s" % (match.groupdict()['date_dispensed'], match.groupdict()['time_dispensed']))
            

if __name__ == "__main__":
    '''
    parseXfdLog_dispenses_by_head.py path_to_log_files [year_of_interest]
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument("path_to_log_files", type=str, help='Path to log file folder')
    parser.add_argument("year_of_interest", type=str, nargs='?', default=dt.date.today().strftime("%Y"), help='Year of log files that you want to parse, wildcards accepted (default is current year)')
    args = parser.parse_args()

    if args.path_to_log_files:
        glob_spec = "%s/xfd.log.%s*" % (os.path.abspath(args.path_to_log_files), args.year_of_interest)
        log_files = sorted(glob.glob(glob_spec))
    else:
        parser.print_help()
        sys.exit(1)

    results_dict = {}
    for log_file in log_files:
        parseXfdLog(log_file, results_dict)
    
    print(results_dict)
    with open('dispenses_by_head.json', 'w') as fp:
        json.dump(results_dict, fp, sort_keys=True, indent=4, separators=(',', ': '), default=set_default)