#!/usr/bin/env python

import sys
import time
import re
import argparse
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import datetime as dt
import collections

# local:
from colors import *

#PrintColors = (BRIGHT_WHITE, WHITE)
PrintColors = (WHITE, WHITE)

def parseSSLog(ss_log, output_path, pdf_path, generic=False):
    '''
    import re
    p = re.compile(ur'../../15\ (?P<start_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] Calling (?P<func_name>[a-zA-Z]*).*?\n../../15\ (?P<end_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] [Call(s)]* success!', re.DOTALL)
    test_str = u"09/29/15 20:28:13.769: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.770: (CommandProcessor) [DEBUG] Reply ID: 23 msg size: 68\n09/29/15 20:28:13.771: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetFPGAVersion...\n09/29/15 20:28:13.773: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.775: (CommandProcessor) [DEBUG] Reply ID: 24 msg size: 98\n09/29/15 20:28:13.776: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionSetupEncoderDirectionSEPD: Card=1, SEPD=2, Value=0\n09/29/15 20:28:13.777: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.778: (CommandProcessor) [DEBUG] Reply ID: 25 msg size: 81\n09/29/15 20:28:13.779: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionSetEncoderDivide...\n09/29/15 20:28:13.783: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.784: (CommandProcessor) [DEBUG] Reply ID: 26 msg size: 97\n09/29/15 20:28:13.785: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionEncoderPulseMultiplySEPD: Card=1, SEPD=2, Value=9\n09/29/15 20:28:13.789: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.790: (CommandProcessor) [DEBUG] Reply ID: 27 msg size: 92\n09/29/15 20:28:13.791: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionPDNoReverseSEPD: Card=1, SEPD=2, Value=0\n09/29/15 20:28:13.792: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.793: (CommandProcessor) [DEBUG] Reply ID: 28 msg size: 45\n09/29/15 20:28:13.794: (XaarCmdAPI      ) [DEBUG] Calling XaarScorpionGetXUSBCount...\n09/29/15 20:28:13.795: (CommandProcessor) [DEBUG] Reply ID: 29 msg size: 98\n09/29/15 20:28:13.796: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionHeadPowerControl...\n09/29/15 20:28:13.809: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.810: (CommandProcessor) [DEBUG] Reply ID: 30 msg size: 62\n09/29/15 20:28:13.811: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetUsbOk...\n09/29/15 20:28:13.812: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.813: (CommandProcessor) [DEBUG] Reply ID: 31 msg size: 98\n09/29/15 20:28:13.814: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionHeadPowerControl...\n09/29/15 20:28:13.828: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.829: (CommandProcessor) [DEBUG] Reply ID: 32 msg size: 62\n09/29/15 20:28:13.830: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetUsbOk...\n09/29/15 20:28:13.831: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.833: (CommandProcessor) [DEBUG] Reply ID: 33 msg size: 133\n09/29/15 20:28:13.834: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetHeadType.  Cards: 12, Heads: 8\n09/29/15 20:28:13.834: (XaarCmdAPI      ) [DEBUG] Call(s) success!\n09/29/15 20:28:13.838: (CommandProcessor) [DEBUG] Reply ID: 34 msg size: 74\n09/29/15 20:28:13.839: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetHeadType...\n09/29/15 20:28:13.840: (CommandProcessor) [DEBUG] Reply ID: 35 msg size: 76\n09/29/15 20:28:13.841: (XaarCmdAPI      ) [DEBUG] Calling bXaarScorpionGetHeadSerial...\n09/29/15 20:28:13.857: (XaarCmdAPI      ) [DEBUG] Call success!\n09/29/15 20:28:13.859: (CommandProcessor) [DEBUG] Reply ID: 36 msg size: 164\n"
     
    re.findall(p, test_str)
    '''
        
    SSCalls_pattern=ur'../../15\ (?P<start_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] Calling (?P<func_name>[a-zA-Z]*).*?\n../../15\ (?P<end_ts>[0-9:.]*): \(XaarCmdAPI      \) \[DEBUG\] [Call(s)]* success'

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
        delta_ms = float(time_delta.total_seconds() * 1000.0)
        if delta_ms <= 0:
            delta_ms = 0.5
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
        deltas_np = np.array(func_deltas_ordered[k])
        func_metrics[k] = []
        func_metrics[k].append( len(deltas_np) )
        func_metrics[k].append( deltas_np.max() )
        func_metrics[k].append( deltas_np.min() )
        func_metrics[k].append( deltas_np.mean() )
        func_metrics[k].append( deltas_np.std() )
    func_metrics_ordered = collections.OrderedDict(sorted(func_metrics.items()))

    print "%s---------------------------------------------------------------------------------------------------------------%s" % (BRIGHT_WHITE, RESET)
    print "%s Scorpion                                                     Sample       Max      Min      Mean     Stdev    %s" % (BRIGHT_WHITE, RESET)
    print "%s Func name                                                     Count      (ms)     (ms)      (ms)      (ms)    %s" % (BRIGHT_WHITE, RESET)
    print "%s---------------------------------------------------------------------------------------------------------------%s" % (BRIGHT_WHITE, RESET)
    idx = 0
    for k in func_metrics_ordered.keys():
        print("%s%-57s  %9d   %7.1f  %7.1f   %7.1f   %7.1f %s" % 
            (PrintColors[idx%2], k, func_metrics_ordered[k][0], func_metrics_ordered[k][1], func_metrics_ordered[k][2], 
             func_metrics_ordered[k][3], func_metrics_ordered[k][4], RESET))
        idx+=1
    
    print("\nNow creating histograms for each function, see %s" % pdf_path)

    with PdfPages(pdf_path) as pdf:
        d = pdf.infodict()
        d['Title'] = u'ScorpionDLL v6.2 FunctionTiming'
        d['Author'] = u'Tom H. Rafferty / CNT'
        d['Subject'] = u'ScorpionDLL v6.2 FunctionTiming'
        d['CreationDate'] = dt.datetime.today()
        d['ModDate'] = dt.datetime.today()

        bins = 100
        for k in func_deltas_ordered.keys():
            deltas_np = np.array(func_deltas_ordered[k])
            max = deltas_np.max()
            min = deltas_np.min()
            if max > bins: 
                binL = min
                binH = max
            else:
                binL = 0
                binH = bins

            #fig = plt.figure(figsize=(10*2,5))
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_title('Histogram: %s' % k)
            ax.set_ylabel('Bin Count')
            ax.set_xlabel('Call Time (ms)')
            ax.text(0.75, 0.75, "Call Stats:",
                horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
            ax.text(0.75, 0.70, ("n: %d" % (len(deltas_np))),
                horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
            ax.text(0.75, 0.65, ("min: %.2f" % (deltas_np.min())),
                horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
            ax.text(0.75, 0.60, ("max: %.2f" % (deltas_np.max())),
                horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
            ax.text(0.75, 0.55, ("mean: %.2f" % (np.round(deltas_np.mean()))),
                horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
            ax.text(0.75, 0.50, ("stdev: %.2f" % (deltas_np.std())),
                horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)

            ax.hist(deltas_np, bins, [binL, binH])
            # ax.axvline(np.round(deltas_np.mean()), linewidth=2, linestyle='--',  color='g')
            # ax.text(np.round(deltas_np.mean()), 0, "Mean",
            #     horizontalalignment='center',verticalalignment='top')

            # ax.axvline(np.round(deltas_np.max()), linewidth=2, linestyle='--',  color='r')
            # ax.text(np.round(deltas_np.max()), 0, "Max",
            #     horizontalalignment='center',verticalalignment='top')

            # ax.axvline(np.round(deltas_np.min()), linewidth=2, linestyle='--',  color='c')
            # ax.text(np.round(deltas_np.min()), 0, "Min",
            #     horizontalalignment='center',verticalalignment='top')

            # #hist,bins = np.histogram(deltas_np, 50, [0,50])
            # plt.hist(deltas_np,bins,[0,bins])
            # plt.ylim([ 0, max + 2 ])

            # plt.text(bins*.7, max*.8, ("min=%.f" % (np.round(deltas_np.min()))), fontsize=14)
            # plt.text(bins*.7, max*.8, ("max=%.f" % (np.round(deltas_np.max()))), fontsize=14)
            # plt.text(bins*.7, max*.6, ("mean=%.f" % (np.round(deltas_np.mean()))), fontsize=14)
            # plt.text(bins*.7, max*.5, ("stdev=%.f" % (np.round(deltas_np.std()))), fontsize=14)
            # #plt.bar(hist)
            # #plt.xlim([ bins[0], bins[-1] ])
            # plt.title('Histogram: %s' % k)
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()

if __name__ == "__main__":
    '''
    parseSSLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-i', '--in_file', dest='in_file', type=str,
                        help='input file...if not specified then use stdin')
    parser.add_argument('-o', '--output_path', dest='output_path', type=str,
                        help='output path...if not specified then will use /tmp', default='/tmp')
    parser.add_argument('-p', '--pdf_path', dest='pdf_path', type=str,
                        help='pdf path', default='/home/trafferty/ScorpionDLL_FuncCallTiming_Hists.pdf')

    args = parser.parse_args()

    if args.in_file:
        parseSSLog(args.in_file, args.output_path, args.pdf_path)
    else:
        parser.print_help()
        sys.exit(1)
