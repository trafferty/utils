#!/usr/bin/env python

import sys
import time
import re
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

def parseLog(logFile, output_path, generic=False):


    write_voltage_pattern = ur"\n201[567]-..-..\ (?P<start_ts>[0-9:.]*): \(XPM_Dispenser   \) \[DEBUG\] RPC send: {\"id\": [0-9]*, \"method\": \"bXaarScorpionWriteHeadTCParameters\",.*?\}\}\n\n201[567]-..-..\ (?P<end_ts>[0-9:.]*): \(XPM_Dispenser   \) \[DEBUG\] XaarCmdAPI: Calling bXaarScorpionWriteHeadTCParameters"
    write_voltage_pattern = ur"\n201[567]-..-..\ (?P<start_ts>[0-9:.]*): \(XPM_Dispenser   \) \[DEBUG\] RPC send: {\"id\": [0-9]*, \"method\": \"bXaarScorpionLoadWaveformAndDownload\",.*?\}\}\n\n201[567]-..-..\ (?P<end_ts>[0-9:.]*): \(XPM_Dispenser   \) \[DEBUG\] XaarCmdAPI: Calling bXaarScorpionLoadWaveformAndDownload"

    f = open(logFile, 'r')
    buf = f.read()
    f.close()
    print "File (%s) opened and read into buffer, length of buf: %d" % (logFile, len(buf))

    write_voltage_sets = [x.groupdict() for x in re.finditer(write_voltage_pattern, buf, re.DOTALL)]
    print "Parsing log for write_voltage...found %d records." % (len(write_voltage_sets))
    if len(write_voltage_sets) > 0: print " >> Date range: %s - %s" % (write_voltage_sets[0]['start_ts'], write_voltage_sets[-1]['start_ts'])

    timestamp_format = "%H:%M:%S.%f"

    processing_times_lst = []
    for write_voltage_set in write_voltage_sets:
        '''
        [{u'combo_funcs': u'true',
          u'end_ts': u'09:59:09,552',
          u'start_ts': u'09:59:09,533'},
         {u'combo_funcs': u'true',
          u'end_ts': u'09:59:10,099',
          u'start_ts': u'09:59:10,071'},
         {u'combo_funcs': u'false',
          u'end_ts': u'09:48:40,169',
          u'start_ts': u'09:48:40,067'},
         {u'combo_funcs': u'false',
          u'end_ts': u'09:49:02,302',
          u'start_ts': u'09:49:02,208'}]
        '''
        start_ts = dt.datetime.strptime(write_voltage_set['start_ts'], timestamp_format)
        end_ts   = dt.datetime.strptime(write_voltage_set['end_ts'], timestamp_format)
        time_delta = end_ts-start_ts
        delta_ms = time_delta.total_seconds() * 1000
        
        # filter out-liers:
        if delta_ms < 5000 and delta_ms > 10:
            processing_times_lst.append(delta_ms)

    
    processing_times_np = np.array(processing_times_lst)
    
    label = 'Waveform Load Times (ms)'
    fig = plt.figure(figsize=(10*2,5))
    if len(processing_times_lst) > 0:
        plt.plot(processing_times_lst, color='b', label=label)
        plt.hlines(processing_times_np.mean(), 0, len(processing_times_lst), color='r', linewidth=2, linestyle='--')
        plt.text(len(processing_times_lst)-10, processing_times_np.mean()+10, ("mean=%.fms" % (np.round(processing_times_np.mean()))), fontsize=18)
    plt.ylabel('time (ms)')
    plt.title(label)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    '''
    parseLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-i', '--in_file', dest='in_file', type=str,
                        help='input file...if not specified then use stdin')
    parser.add_argument('-o', '--output_path', dest='output_path', type=str,
                        help='output path...if not specified then will use /tmp', default='/tmp')

    args = parser.parse_args()

    if args.in_file:
        parseLog(args.in_file, args.output_path)
    else:
        parser.print_help()
        sys.exit(1)
