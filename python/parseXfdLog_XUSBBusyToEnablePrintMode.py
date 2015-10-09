#!/usr/bin/env python

import sys
import time
import re
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

def parseXfdSSLog(xfdLog, output_path, generic=False):
    '''
    import re
    p = re.compile(ur'2015-..-..\ (?P<start_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.printmanagerXPM -   SetPDInternal.*?Calling bXaarScorpionEnablePrintMode...call success\r\n2015-..-..\ (?P<end_ts>[0-9:,]*)\ INFO', re.DOTALL)
    test_str = u"2015-08-27 20:24:02,442 INFO RequestProcessor-4 xfd.xfdservice - Vector 0 is -13.0525085, -0.0352770499999826 to 17.7094003, -0.0352770499999826\n2015-08-27 20:24:02,462 INFO RequestProcessor-4 xfd.xfdservice - Dispensing pattern for tcs:0 recipe:-1 swathe:0\n2015-08-27 20:24:02,465 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling XaarScorpionAllowGetTemperatures...call success\n2015-08-27 20:24:02,469 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionGetStatusData...call success\n2015-08-27 20:24:02,471 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionGetPCBTemperature...call success\n2015-08-27 20:24:02,475 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionGetStatusData...call success\n2015-08-27 20:24:02,477 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionGetPCBTemperature...call success\n2015-08-27 20:24:02,479 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling XaarScorpionAllowGetTemperatures...call success\n2015-08-27 20:24:02,481 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-08-27 20:24:02,514 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\n2015-08-27 20:24:02,524 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupSwatheBlockParametersUpdated...call success\n2015-08-27 20:24:02,560 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPrintDataParametersUpdated...call success\n2015-08-27 20:24:02,570 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupSwatheBlockParametersUpdated...call success\n2015-08-27 20:24:02,606 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPrintDataParametersUpdated...call success\n2015-08-27 20:24:02,606 INFO RequestProcessor-4 xfd.printmanagerXPM - Setting up DDFS. DDFSValue = 1341370\n2015-08-27 20:24:02,606 INFO RequestProcessor-4 xfd.printmanagerXPM -   swathe.internalEncoderFrequency_Hz = 28347.04149014728\n2015-08-27 20:24:02,606 INFO RequestProcessor-4 xfd.printmanagerXPM -   DDFSMultiplier                     = 0.3356\n2015-08-27 20:24:02,606 INFO RequestProcessor-4 xfd.printmanagerXPM -   cycleMode                          = 3\n2015-08-27 20:24:02,606 INFO RequestProcessor-4 xfd.printmanagerXPM -   encoderDivide                      = 47\n2015-08-27 20:24:02,606 INFO RequestProcessor-4 xfd.printmanagerXPM -   ...DDFSValue (multiplied together) = 1341370\n2015-08-27 20:24:02,611 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetDDFSValueSEPD...call success\n2015-08-27 20:24:02,611 INFO RequestProcessor-4 xfd.printmanagerXPM - Using internal encoder frequency of 28347.04149014728 Hz\n2015-08-27 20:24:02,611 INFO RequestProcessor-4 xfd.printmanagerXPM -   SetDDFSEnable                      = 1\n2015-08-27 20:24:02,615 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetDDFSEnable...call success\n2015-08-27 20:24:02,615 INFO RequestProcessor-4 xfd.printmanagerXPM -   SetPDInternal                      = 0\n2015-08-27 20:24:02,618 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPDInternalSEPD...call success\n2015-08-27 20:24:02,620 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-08-27 20:24:02,622 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-08-27 20:24:02,627 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\n2015-08-27 20:24:02,629 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-08-27 20:34:02,442 INFO RequestProcessor-4 xfd.xfdservice - getDropRecipeSwatheVectors 0 rec:-1\n2015-08-27 20:34:02,442 INFO RequestProcessor-4 xfd.xfdservice - Vector 0 is -13.0525085, -0.0352770499999826 to 17.7094003, -0.0352770499999826\n2015-08-27 20:34:02,464 INFO RequestProcessor-4 xfd.xfdservice - Dispensing pattern for tcs:0 recipe:-1 swathe:0\n2015-08-27 20:34:02,467 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling XaarScorpionAllowGetTemperatures...call success\n2015-08-27 20:34:02,471 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionGetStatusData...call success\n2015-08-27 20:34:02,473 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionGetPCBTemperature...call success\n2015-08-27 20:34:02,477 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionGetStatusData...call success\n2015-08-27 20:34:02,479 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionGetPCBTemperature...call success\n2015-08-27 20:34:02,481 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling XaarScorpionAllowGetTemperatures...call success\n2015-08-27 20:34:02,483 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-08-27 20:34:02,516 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\n2015-08-27 20:34:02,526 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupSwatheBlockParametersUpdated...call success\n2015-08-27 20:34:02,562 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPrintDataParametersUpdated...call success\n2015-08-27 20:34:02,572 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupSwatheBlockParametersUpdated...call success\n2015-08-27 20:34:02,608 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPrintDataParametersUpdated...call success\n2015-08-27 20:34:02,608 INFO RequestProcessor-4 xfd.printmanagerXPM - Setting up DDFS. DDFSValue = 1341370\n2015-08-27 20:34:02,608 INFO RequestProcessor-4 xfd.printmanagerXPM -   swathe.internalEncoderFrequency_Hz = 28347.04149014728\n2015-08-27 20:34:02,608 INFO RequestProcessor-4 xfd.printmanagerXPM -   DDFSMultiplier                     = 0.3356\n2015-08-27 20:34:02,608 INFO RequestProcessor-4 xfd.printmanagerXPM -   cycleMode                          = 3\n2015-08-27 20:34:02,608 INFO RequestProcessor-4 xfd.printmanagerXPM -   encoderDivide                      = 47\n2015-08-27 20:34:02,608 INFO RequestProcessor-4 xfd.printmanagerXPM -   ...DDFSValue (multiplied together) = 1341370\n2015-08-27 20:34:02,613 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetDDFSValueSEPD...call success\n2015-08-27 20:34:02,613 INFO RequestProcessor-4 xfd.printmanagerXPM - Using internal encoder frequency of 28347.04149014728 Hz\n2015-08-27 20:34:02,613 INFO RequestProcessor-4 xfd.printmanagerXPM -   SetDDFSEnable                      = 1\n2015-08-27 20:34:02,617 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetDDFSEnable...call success\n2015-08-27 20:34:02,617 INFO RequestProcessor-4 xfd.printmanagerXPM -   SetPDInternal                      = 0\n2015-08-27 20:34:02,620 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPDInternalSEPD...call success\n2015-08-27 20:34:02,622 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-08-27 20:34:02,624 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-08-27 20:34:02,629 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\n2015-08-27 20:34:02,631 INFO RequestProcessor-4 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-08-27 20:44:02,444 INFO RequestProcessor-4 xfd.xfdservice - getDropRecipeSwatheVectors 0 rec:-1\n2015-08-27 20:44:02,444 INFO RequestProcessor-4 xfd.xfdservice - Vector 0 is -13.0525085, -0.0352770499999826 to 17.7094003, -0.0352770499999826\n2015-08-27 20:44:02,461 INFO RequestProcessor-4 xfd.xfdservice - Dispensing pattern for tcs:0 recipe:-1 swathe:0\n:\n"
     
    re.findall(p, test_str)   
    '''
        
    XUSBBusyToEnablePrintMode_pattern=ur'2015-..-..\ (?P<start_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.printmanagerXPM -   SetPDInternal.*?Calling bXaarScorpionEnablePrintMode...call success\r\n2015-..-..\ (?P<end_ts>[0-9:,]*)\ INFO'

    f = open(xfdLog, 'r')
    buf = f.read()
    f.close()
    print "File (%s) opened and read into buffer, length of buf: %d" % (xfdLog, len(buf))

    #XUSBBusy_sets = [x.groupdict() for x in re.finditer(XUSBBusy_pattern, buf, re.DOTALL)]
    XUSBBusyToEnablePrintMode_sets = [x.groupdict() for x in re.finditer(XUSBBusyToEnablePrintMode_pattern, buf, re.DOTALL)]
    print "Parsing log for XUSBBusyToEnablePrintMode calls...found %d records." % (len(XUSBBusyToEnablePrintMode_sets))
    if len(XUSBBusyToEnablePrintMode_sets) > 0: print " >> Date range: %s - %s" % (XUSBBusyToEnablePrintMode_sets[0]['start_ts'], XUSBBusyToEnablePrintMode_sets[-1]['start_ts'])

    timestamp_format = "%H:%M:%S,%f"

    processing_times_XUSBBusyToEnablePrintMode = []
    for XUSBBusyToEnablePrintMode_set in XUSBBusyToEnablePrintMode_sets:
        '''
        [{u'end_ts': u'20:24:02,481', u'start_ts': u'20:24:02,442'},
         {u'end_ts': u'20:24:02,620', u'start_ts': u'20:24:02,514'},
         {u'end_ts': u'20:24:02,629', u'start_ts': u'20:24:02,622'},
         {u'end_ts': u'20:34:02,483', u'start_ts': u'20:34:02,442'},
         {u'end_ts': u'20:34:02,622', u'start_ts': u'20:34:02,516'},
         {u'end_ts': u'20:34:02,631', u'start_ts': u'20:34:02,624'}]
        '''
        start_ts = dt.datetime.strptime(XUSBBusyToEnablePrintMode_set['start_ts'], timestamp_format)
        end_ts   = dt.datetime.strptime(XUSBBusyToEnablePrintMode_set['end_ts'], timestamp_format)
        time_delta = end_ts-start_ts
        delta_ms = time_delta.total_seconds() * 1000
        processing_times_XUSBBusyToEnablePrintMode.append(delta_ms)
    
    processing_times_XUSBBusyToEnablePrintMode_np = np.array(processing_times_XUSBBusyToEnablePrintMode)
    
    if len(processing_times_XUSBBusyToEnablePrintMode) == 0:
        return
        
    fig = plt.figure(figsize=(10*2,5))
    ax = fig.add_subplot(111)
    ax.set_title('XUSBBusy -> EnablePrintMode: call timing')
    ax.set_ylabel('time (ms)')
    ax.text(0.55, 0.75, ("mean=%.f" % (np.round(processing_times_XUSBBusyToEnablePrintMode_np.mean()))),
        horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
    ax.text(0.55, 0.70, ("stdev=%.2f" % (processing_times_XUSBBusyToEnablePrintMode_np.std())),
        horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
    ax.text(0.55, 0.65, ("max=%.2f" % (processing_times_XUSBBusyToEnablePrintMode_np.max())),
        horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
    ax.text(0.55, 0.60, ("min=%.2f" % (processing_times_XUSBBusyToEnablePrintMode_np.min())),
        horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
    ax.hlines(processing_times_XUSBBusyToEnablePrintMode_np.mean(), 0, len(processing_times_XUSBBusyToEnablePrintMode), color='r', linewidth=2, linestyle='--')
    ax.plot(processing_times_XUSBBusyToEnablePrintMode, color='b')
    
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
        parseXfdSSLog(args.in_file, args.output_path)
    else:
        parser.print_help()
        sys.exit(1)
