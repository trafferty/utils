#!/usr/bin/env python

import sys
import re
import math
import datetime as dt
import collections

def calc_mean_stdev(value_lst):
    try:
        std = []
        for value in value_lst:
            std.append(pow((value - (sum(value_lst)/len(value_lst))), 2))
        stdev = math.sqrt(sum(std)/len(std))
        mean = (sum(value_lst)/len(value_lst))
        return float(mean), float(stdev)
    except:
        print "invalid input"
        return 0, 0

def getKey(item):
        return item[3]

def parseSSLog(ss_log):
    '''
    Reads ScorpionServer log file, parses using regex to find all calls to ScorpionDLL, then
    calculates metrics (min, max, mean, stdev) for the call's elapsed times.
    '''

    f = open(ss_log, 'r')
    buf = f.read()
    f.close()
    print "File (%s) opened and read into buffer, length of buf: %d" % (ss_log, len(buf))

    SSCalls_pattern=ur'../../15\ (?P<start_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] Calling (?P<func_name>[a-zA-Z]*).*?\n../../15\ (?P<end_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] [Call(s)]* success'
    SSCalls_sets = [x.groupdict() for x in re.finditer(SSCalls_pattern, buf, re.DOTALL)]
    print "Parsing log for SSCalls calls...found %d records." % (len(SSCalls_sets))

    timestamp_format = "%H:%M:%S.%f"

    processing_times_SSCalls = []
    for SSCalls_set in SSCalls_sets:
        '''
        SSCalls_set should look something like this:
        [{u'end_ts': u'20:28:13.773',u'func_name': u'bXaarScorpionGetFPGAVersion',u'start_ts': u'20:28:13.771'},
         {u'end_ts': u'20:28:13.777',u'func_name': u'bXaarScorpionSetupEncoderDirectionSEPD',u'start_ts': u'20:28:13.776'},
            ...
        {u'end_ts': u'20:28:13.857',u'func_name': u'bXaarScorpionGetHeadType', u'start_ts': u'20:28:13.839'}]
        '''
        start_ts = dt.datetime.strptime(SSCalls_set['start_ts'], timestamp_format)
        func_name= SSCalls_set['func_name']
        end_ts   = dt.datetime.strptime(SSCalls_set['end_ts'], timestamp_format)
        time_delta = end_ts-start_ts
        delta_ms = float(time_delta.total_seconds() * 1000.0)
        if delta_ms <= 0:
            delta_ms = 1.0
        processing_times_SSCalls.append( (func_name, delta_ms) )

    if len(processing_times_SSCalls) == 0:
        return

    func_deltas = {}
    for processing_time in processing_times_SSCalls:
        func_name = processing_time[0]
        delta     = processing_time[1]
        if func_name not in func_deltas:
            func_deltas[func_name] = []
        func_deltas[func_name].append(delta)
    func_deltas_ordered = collections.OrderedDict(sorted(func_deltas.items()))

    func_metrics = {}
    for k in func_deltas_ordered.keys():
        func_metrics[k] = []
        mean, stdev = calc_mean_stdev(func_deltas_ordered[k])
        func_metrics[k].append( len(func_deltas_ordered[k]) )
        func_metrics[k].append( max(func_deltas_ordered[k]) )
        func_metrics[k].append( min(func_deltas_ordered[k]) )
        func_metrics[k].append( mean )
        func_metrics[k].append( stdev )
    func_metrics_ordered = collections.OrderedDict(sorted(func_metrics.items()))

    print "---------------------------------------------------------------------------------------------------------------"
    print " Scorpion                                                     Sample       Max      Min      Mean     Stdev    "
    print " Func name                                                     Count      (ms)     (ms)      (ms)      (ms)    "
    print "---------------------------------------------------------------------------------------------------------------"
    for k in func_metrics_ordered.keys():
        print("%-57s  %9d   %7.1f  %7.1f   %7.1f   %7.1f" % 
            (k, func_metrics_ordered[k][0], func_metrics_ordered[k][1], func_metrics_ordered[k][2],
             func_metrics_ordered[k][3], func_metrics_ordered[k][4]))

if __name__ == "__main__":
    '''
    parseSSLog_allCalls_xaar.py path_to_log_file
    '''
    if len(sys.argv) == 2:
        parseSSLog(sys.argv[1])
    else:
        print "\nparseSSLog_allCalls_xaar.py - Parse ScorpionServer log, calculate metrics\n"
        print "  Syntax:"
        print "     python parseSSLog_allCalls_xaar.py path_to_log_file"
