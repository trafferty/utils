#!/usr/bin/env python

import sys
import time
import re
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

# local:
from colors import *

#PrintColors = (BRIGHT_YELLOW, BRIGHT_CYAN)
PrintColors = (WHITE, WHITE)

def parseSSLog(ss_log, output_path, generic=False):
    '''
    import re
    p = re.compile(ur'../../15\ (?P<start_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] Calling (?P<func_name>[a-zA-Z]*).*?\n../../15\ (?P<end_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] [Call(s)]* success!', re.DOTALL)
    test_str = u"09/29/15 20:28:13.769: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.770: (CommandProcessor) [DEBUG] Reply ID: 23 msg size: 68\n09/29/15 20:28:13.771: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetFPGAVersion...\n09/29/15 20:28:13.773: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.775: (CommandProcessor) [DEBUG] Reply ID: 24 msg size: 98\n09/29/15 20:28:13.776: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionSetupEncoderDirectionSEPD: Card=1, SEPD=2, Value=0\n09/29/15 20:28:13.777: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.778: (CommandProcessor) [DEBUG] Reply ID: 25 msg size: 81\n09/29/15 20:28:13.779: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionSetEncoderDivide...\n09/29/15 20:28:13.783: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.784: (CommandProcessor) [DEBUG] Reply ID: 26 msg size: 97\n09/29/15 20:28:13.785: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionEncoderPulseMultiplySEPD: Card=1, SEPD=2, Value=9\n09/29/15 20:28:13.789: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.790: (CommandProcessor) [DEBUG] Reply ID: 27 msg size: 92\n09/29/15 20:28:13.791: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionPDNoReverseSEPD: Card=1, SEPD=2, Value=0\n09/29/15 20:28:13.792: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.793: (CommandProcessor) [DEBUG] Reply ID: 28 msg size: 45\n09/29/15 20:28:13.794: (XaarCmdAPI      ) [DEBUG] Calling XaarScorpionGetXUSBCount...\n09/29/15 20:28:13.795: (CommandProcessor) [DEBUG] Reply ID: 29 msg size: 98\n09/29/15 20:28:13.796: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionHeadPowerControl...\n09/29/15 20:28:13.809: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.810: (CommandProcessor) [DEBUG] Reply ID: 30 msg size: 62\n09/29/15 20:28:13.811: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetUsbOk...\n09/29/15 20:28:13.812: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.813: (CommandProcessor) [DEBUG] Reply ID: 31 msg size: 98\n09/29/15 20:28:13.814: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionHeadPowerControl...\n09/29/15 20:28:13.828: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.829: (CommandProcessor) [DEBUG] Reply ID: 32 msg size: 62\n09/29/15 20:28:13.830: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetUsbOk...\n09/29/15 20:28:13.831: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.833: (CommandProcessor) [DEBUG] Reply ID: 33 msg size: 133\n09/29/15 20:28:13.834: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetHeadType.  Cards: 12, Heads: 8\n09/29/15 20:28:13.834: (XaarCmdAPI      ) [DEBUG] Call(s) success!\n09/29/15 20:28:13.838: (CommandProcessor) [DEBUG] Reply ID: 34 msg size: 74\n09/29/15 20:28:13.839: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetHeadType...\n09/29/15 20:28:13.840: (CommandProcessor) [DEBUG] Reply ID: 35 msg size: 76\n09/29/15 20:28:13.841: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetHeadSerial...\n09/29/15 20:28:13.857: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.859: (CommandProcessor) [DEBUG] Reply ID: 36 msg size: 164\n"
     
    re.findall(p, test_str)
    '''
        
    SSCalls_pattern=ur'../../15\ (?P<start_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] Calling (?P<func_name>[a-zA-Z]*).*?\n../../15\ (?P<end_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] [Call(s)]* success!'

    f = open(ss_log, 'r')
    buf = f.read()
    f.close()
    print "File (%s) opened and read into buffer, length of buf: %d" % (ss_log, len(buf))

    SSCalls_sets = [x.groupdict() for x in re.finditer(SSCalls_pattern, buf, re.DOTALL)]
    print "Parsing log for SSCalls calls...found %d records." % (len(SSCalls_sets))
    if len(SSCalls_sets) > 0: print " >> Date range: %s - %s" % (SSCalls_sets[0]['start_ts'], SSCalls_sets[-1]['start_ts'])

    timestamp_format = "%H:%M:%S.%f"

    processing_times_SSCalls = []
    for SSCalls_set in SSCalls_sets:
        '''
        [{u'end_ts': u'20:28:13.773',u'func_name': u'bXaarScorpionGetFPGAVersion',u'start_ts': u'20:28:13.771'},
         {u'end_ts': u'20:28:13.777',u'func_name': u'bXaarScorpionSetupEncoderDirectionSEPD',u'start_ts': u'20:28:13.776'},
            ...     
        {u'end_ts': u'20:28:13.857',u'func_name': u'bXaarScorpionGetHeadType', u'start_ts': u'20:28:13.839'}]
        '''
        start_ts = dt.datetime.strptime(SSCalls_set['start_ts'], timestamp_format)
        func_name= SSCalls_set['func_name']
        end_ts   = dt.datetime.strptime(SSCalls_set['end_ts'], timestamp_format)
        time_delta = end_ts-start_ts
        delta_ms = time_delta.total_seconds() * 1000
        if delta_ms == 0: delta_ms = 0.5
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

    func_metrics = {}
    for k in func_deltas.keys():
        deltas_np = np.array(func_deltas[k])
        func_metrics[k] = []
        func_metrics[k].append( len(deltas_np) )
        func_metrics[k].append( deltas_np.max() )
        func_metrics[k].append( deltas_np.min() )
        func_metrics[k].append( deltas_np.mean() )

    print "%s-------------------------------------------------------------------------------------------------%s" % (WHITE, RESET)
    print "%s Scorpion                                                     Sample     Max      Min      Mean  %s" % (WHITE, RESET)
    print "%s func                                                         cnt        (ms)     (ms)     (ms)  %s" % (WHITE, RESET)
    print "%s-------------------------------------------------------------------------------------------------%s" % (WHITE, RESET)
    idx = 0
    for k in func_metrics.keys():
        print("%s%-60s  %-9d  %-7d  %-7d  %-7d %s" % 
            (PrintColors[idx%2], k, func_metrics[k][0], func_metrics[k][1], func_metrics[k][2], func_metrics[k][3],
             RESET))
        idx+=1

if __name__ == "__main__":
    '''
    parseSSLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-i', '--in_file', dest='in_file', type=str,
                        help='input file...if not specified then use stdin')
    parser.add_argument('-o', '--output_path', dest='output_path', type=str,
                        help='output path...if not specified then will use /tmp', default='/tmp')

    args = parser.parse_args()

    if args.in_file:
        parseSSLog(args.in_file, args.output_path)
    else:
        parser.print_help()
        sys.exit(1)
