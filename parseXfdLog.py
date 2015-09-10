#!/usr/bin/env python

import sys
import time
import re
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import time
import operator
from collections import defaultdict
from collections import OrderedDict

def parseXfdLog(xfdLog, output_path, generic=False):
    '''
    2015-09-02 09:48:40,067 INFO RequestProcessor-5 xfd.DispenseHeadXpm - UseXPMComboFunctions defaulting to: false
    2015-09-02 09:48:40,079 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupSwatheBlockParametersUpdated...call success
    2015-09-02 09:48:40,119 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPrintDataParametersUpdated...call success
    2015-09-02 09:48:40,129 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupSwatheBlockParametersUpdated...call success
    2015-09-02 09:48:40,168 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPrintDataParametersUpdated...call success
    2015-09-02 09:48:40,168 INFO RequestProcessor-5 xfd.printmanagerXPM - Setting up DDFS. DDFSValue = 1341370
    2015-09-02 09:48:40,169 INFO RequestProcessor-5 xfd.printmanagerXPM -   swathe.internalEncoderFrequency_Hz = 28347.04149014728
    '''
    
    '''
    test patterns:
    2015.*?\ (?P<start_ts>[0-9:,]*)\ INFO.*?getDropRecipeSwatheVectors.*?Dispensing\ pattern\ for\ tcs:.\ recipe:(?P<recipe>[0-9]*)\ swathe:(?P<swathe>[0-9]*).*?UseXPMComboFunctions:\ (?P<combo_funcs>[truefals]*)
    
    UseXPMComboFunctions[defaulting\ to:]*\ (?P<combo_funcs>[truefals]*).*?2015.*?\ (?P<start_ts>[0-9:,]*)\ INFO.*?
    
    2015.*?\ (?P<start_ts>[0-9:,]*)\ INFO.*?UseXPMComboFunctions[defaulting\ to:]*\ (?P<combo_funcs>[truefals]*).*?
   
    2015-..-..\ (?P<start_ts>[0-9:,]*)\ INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpion_loadControlBlock_Combo.*?DDFS. DDFSValue = [0-9]*\n2015-..-..\ (?P<end_ts>[0-9:,]*)\ INFO 
    
    2015-..-..\ (?P<start_ts>[0-9:,]*)\ INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpion_loadControlBlock_Combo.*?\n2015-..-..\ (?P<end_ts>[0-9:,]*)\ INFO
    
    Works! (https://regex101.com/r/yN1zL7/3#python): 
    p = re.compile(ur'2015-..-..\ (?P<start_ts>[0-9:,]*)\ INFO RequestProcessor-5 xfd.DispenseHeadXpm - UseXPMComboFunctions[defaulting\ to:]*\ (?P<combo_funcs>[truefals]*).*?DDFS. DDFSValue = [0-9]*\n2015-..-..\ (?P<end_ts>[0-9:,]*)\ INFO', re.DOTALL)
   
    '''

    #~ combo_function_pattern = r'''
        #~ 2015-..-..\ (?P<start_ts>[0-9:,]*)\ INFO RequestProcessor-5 xfd.DispenseHeadXpm - UseXPMComboFunctions[defaulting\ to:]*\ (?P<combo_funcs>[truefals]*).*?
        #~ DDFS. DDFSValue = [0-9]*\r\n2015-..-..\ (?P<end_ts>[0-9:,]*)\ INFO
        #~ '''
        
    combo_function_pattern=ur'2015-..-..\ (?P<start_ts>[0-9:,]*)\ INFO RequestProcessor-5 xfd.DispenseHeadXpm - UseXPMComboFunctions[defaulting\ to:]*\ (?P<combo_funcs>[truefals]*).*?DDFS. DDFSValue = [0-9]*\r\n2015-..-..\ (?P<end_ts>[0-9:,]*)\ INFO'

    non_combo_pattern = ur'2015-..-..\ (?P<start_ts>[0-9:,]*)\ INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupSwatheBlockParametersUpdated.*?DDFS\.\ DDFSValue\ =\ [0-9]*\r\n2015-..-..\ (?P<end_ts>[0-9:,]*)\ INFO'

    f = open(xfdLog, 'r')
    buf = f.read()
    f.close()
    print "File (%s) opened and read into buffer, length of buf: %d" % (xfdLog, len(buf))

    combo_function_sets = [x.groupdict() for x in re.finditer(combo_function_pattern, buf, re.DOTALL)]
    print "Parsing log for combo/non-combo...found %d records." % (len(combo_function_sets))
    if len(combo_function_sets) > 0: print " >> Date range: %s - %s" % (combo_function_sets[0]['start_ts'], combo_function_sets[-1]['start_ts'])

    non_combo_sets = [x.groupdict() for x in re.finditer(non_combo_pattern, buf, re.DOTALL)]
    print "Parsing log for combo/non-combo...found %d records." % (len(non_combo_sets))
    if len(non_combo_sets) > 0: print " >> Date range: %s - %s" % (non_combo_sets[0]['start_ts'], non_combo_sets[-1]['start_ts'])

    timestamp_format = "%H:%M:%S,%f"

    processing_times_combo = []
    processing_times_nocombo = []
    for combo_function_set in combo_function_sets:
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
        start_ts = dt.datetime.strptime(combo_function_set['start_ts'], timestamp_format)
        end_ts   = dt.datetime.strptime(combo_function_set['end_ts'], timestamp_format)
        time_delta = end_ts-start_ts
        delta_ms = time_delta.total_seconds() * 1000
        
        if combo_function_set['combo_funcs'] == 'true':
            processing_times_combo.append(delta_ms)
        else:
            processing_times_nocombo.append(delta_ms)

    for non_combo_set in non_combo_sets:
        start_ts = dt.datetime.strptime(non_combo_set['start_ts'], timestamp_format)
        end_ts   = dt.datetime.strptime(non_combo_set['end_ts'], timestamp_format)
        time_delta = end_ts-start_ts
        delta_ms = time_delta.total_seconds() * 1000
        processing_times_nocombo.append(delta_ms)
        
    fig = plt.figure(figsize=(10*2,5))
    if len(processing_times_combo) > 0:
        plt.plot(processing_times_combo, label='Combo Funcs')
    if len(processing_times_nocombo) > 0:
        plt.plot(processing_times_nocombo, label='No Combo Funcs')
    plt.title('Combo vs Non-Combo')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    '''
    parseXfdLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-i', '--in_file', dest='in_file', type=str,
                        help='input file...if not specified then use stdin')
    parser.add_argument('-o', '--output_path', dest='output_path', type=str,
                        help='output path...if not specified then will use /tmp', default='/tmp')

    args = parser.parse_args()

    if args.in_file:
        parseXfdLog(args.in_file, args.output_path)
    else:
        parser.print_help()
        sys.exit(1)
