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
    p = re.compile(ur'Vector 1 is.*?\n201[56]-..-..\ (?P<start1_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.xfdservice - Dispensing pattern for tcs:. recipe:. swathe:0.*?\n201[56]-..-..\ (?P<end1_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n201[56]-..-..\ (?P<start2_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.xfdservice - Dispensing pattern for tcs:. recipe:. swathe:1.*?\n201[56]-..-..\ (?P<fake_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\n201[56]-..-..\ (?P<end2_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n', re.DOTALL)
    test_str = u"2015-09-02 09:59:09,355 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSelectSEPD...call success\n2015-09-02 09:59:09,359 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionReloadAppXMLFileParameters...call success\n2015-09-02 09:59:09,362 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling XaarScorpionGetMaxHeadBlocksXPM...call success\n2015-09-02 09:59:09,372 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupImageDataParametersUpdated...call success\n2015-09-02 09:59:09,384 INFO RequestProcessor-5 xfd.DispenseHeadXpm - Head 1014349 row 1 had 0 drops, row 2 had 28665 drops after rows were swapped.\n2015-09-02 09:59:09,399 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPrintDataUpdated...call success\n2015-09-02 09:59:09,399 INFO RequestProcessor-5 xfd.printmanagerXPM - Loading swathe 1 of 1\n2015-09-02 09:59:09,399 INFO RequestProcessor-5 xfd.DispenseHeadXpm - loadBitmap:     = 128, colCount = 741, totalSize = 94848\n2015-09-02 09:59:09,400 INFO RequestProcessor-5 xfd.DispenseHeadXpm - XPMSEPDSetup: 3\n2015-09-02 09:59:09,406 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSelectSEPD...call success\n2015-09-02 09:59:09,410 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionReloadAppXMLFileParameters...call success\n2015-09-02 09:59:09,414 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling XaarScorpionGetMaxHeadBlocksXPM...call success\n2015-09-02 09:59:09,425 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupImageDataParametersUpdated...call success\n2015-09-02 09:59:09,437 INFO RequestProcessor-5 xfd.DispenseHeadXpm - Head 1014349 row 1 had 0 drops, row 2 had 28536 drops after rows were swapped.\n2015-09-02 09:59:09,454 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPrintDataUpdated...call success\n2015-09-02 09:59:09,488 INFO RequestProcessor-5 xfd.xfdservice - getDropRecipeSwatheVectors 0 rec:0\n2015-09-02 09:59:09,489 INFO RequestProcessor-5 xfd.xfdservice - Vector 0 is -13.017231449999999, -4.97406405 to 17.727038825, -4.97406405\n2015-09-02 09:59:09,489 INFO RequestProcessor-5 xfd.xfdservice - Vector 1 is 18.057147025, -4.97406405 to -12.704761775000001, -4.97406405\n2015-09-02 09:59:09,496 INFO RequestProcessor-5 xfd.xfdservice - Dispensing pattern for tcs:0 recipe:0 swathe:0\n2015-09-02 09:59:09,498 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-09-02 09:59:09,533 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\n2015-09-02 09:59:09,533 INFO RequestProcessor-5 xfd.DispenseHeadXpm - UseXPMComboFunctions: true\n2015-09-02 09:59:09,551 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpion_loadControlBlock_Combo...call success\n2015-09-02 09:59:09,552 INFO RequestProcessor-5 xfd.printmanagerXPM - Setting up DDFS. DDFSValue = 1341370\n2015-09-02 09:59:09,552 INFO RequestProcessor-5 xfd.printmanagerXPM -   swathe.internalEncoderFrequency_Hz = 28347.04149014728\n2015-09-02 09:59:09,552 INFO RequestProcessor-5 xfd.printmanagerXPM -   DDFSMultiplier                     = 0.3356\n2015-09-02 09:59:09,552 INFO RequestProcessor-5 xfd.printmanagerXPM -   cycleMode                          = 3\n2015-09-02 09:59:09,552 INFO RequestProcessor-5 xfd.printmanagerXPM -   encoderDivide                      = 47\n2015-09-02 09:59:09,552 INFO RequestProcessor-5 xfd.printmanagerXPM -   ...DDFSValue (multiplied together) = 1341370\n2015-09-02 09:59:09,557 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetDDFSValueSEPD...call success\n2015-09-02 09:59:09,557 INFO RequestProcessor-5 xfd.printmanagerXPM - Using internal encoder frequency of 28347.04149014728 Hz\n2015-09-02 09:59:09,557 INFO RequestProcessor-5 xfd.printmanagerXPM -   SetDDFSEnable                      = 1\n2015-09-02 09:59:09,561 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetDDFSEnable...call success\n2015-09-02 09:59:09,561 INFO RequestProcessor-5 xfd.printmanagerXPM -   SetPDInternal                      = 0\n2015-09-02 09:59:09,564 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPDInternalSEPD...call success\n2015-09-02 09:59:09,566 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-09-02 09:59:09,568 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-09-02 09:59:09,573 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\n2015-09-02 09:59:09,575 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-09-02 09:59:10,035 INFO RequestProcessor-5 xfd.xfdservice - Dispensing pattern for tcs:0 recipe:0 swathe:1\n2015-09-02 09:59:10,038 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-09-02 09:59:10,071 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\n2015-09-02 09:59:10,071 INFO RequestProcessor-5 xfd.DispenseHeadXpm - UseXPMComboFunctions: true\n2015-09-02 09:59:10,098 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpion_loadControlBlock_Combo...call success\n2015-09-02 09:59:10,099 INFO RequestProcessor-5 xfd.printmanagerXPM - Setting up DDFS. DDFSValue = 1341370\n2015-09-02 09:59:10,099 INFO RequestProcessor-5 xfd.printmanagerXPM -   swathe.internalEncoderFrequency_Hz = 28347.04149014728\n2015-09-02 09:59:10,099 INFO RequestProcessor-5 xfd.printmanagerXPM -   DDFSMultiplier                     = 0.3356\n2015-09-02 09:59:10,099 INFO RequestProcessor-5 xfd.printmanagerXPM -   cycleMode                          = 3\n2015-09-02 09:59:10,099 INFO RequestProcessor-5 xfd.printmanagerXPM -   encoderDivide                      = 47\n2015-09-02 09:59:10,099 INFO RequestProcessor-5 xfd.printmanagerXPM -   ...DDFSValue (multiplied together) = 1341370\n2015-09-02 09:59:10,104 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetDDFSValueSEPD...call success\n2015-09-02 09:59:10,104 INFO RequestProcessor-5 xfd.printmanagerXPM - Using internal encoder frequency of 28347.04149014728 Hz\n2015-09-02 09:59:10,104 INFO RequestProcessor-5 xfd.printmanagerXPM -   SetDDFSEnable                      = 1\n2015-09-02 09:59:10,109 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetDDFSEnable...call success\n2015-09-02 09:59:10,109 INFO RequestProcessor-5 xfd.printmanagerXPM -   SetPDInternal                      = 0\n2015-09-02 09:59:10,112 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPDInternalSEPD...call success\n2015-09-02 09:59:10,114 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-09-02 09:59:10,116 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-09-02 09:59:10,120 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\n2015-09-02 09:59:10,122 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\n2015-09-02 10:00:05,341 INFO RequestProcessor-5 xfd.xfdservice - setDenseDropRecipes 0 count:0\n2015-09-02 10:00:05,342 INFO RequestProcessor-5 xfd.xfdservice - Drop patterns loaded and ready for dispense.\n2015-09-02 10:00:05,403 WARN RequestProcessor-5 xfd.xfdservice - No fluidType Specified, using first headgroup\n2015-09-02 10:00:05,403 INFO RequestProcessor-5 xfd.xfdservice - Dispensing with headGroup 0\n2015-09-02 10:00:05,415 INFO RequestProcessor-5 xfd.xfdservice - Successfully generated 2 swathes for pattern.\n2015-09-02 10:00:05,415 INFO RequestProcessor-5 xfd.printmanagerXPM - Loading swathe 1 of 1\n2015-09-02 10:00:05,416 INFO RequestProcessor-5 xfd.DispenseHeadXpm - loadBitmap:     = 128, colCount = 741, totalSize = 94848\n2015-09-02 10:00:05,416 INFO RequestProcessor-5 xfd.DispenseHeadXpm - XPMSEPDSetup: 3\n2015-09-02 10:00:05,421 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSelectSEPD...call success\n2015-09-02 10:00:05,424 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionReloadAppXMLFileParameters...call success\n2015-09-02 10:00:05,427 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling XaarScorpionGetMaxHeadBlocksXPM...call success\n2015-09-02 10:00:05,436 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupImageDataParametersUpdated...call success\n2015-09-02 10:00:05,447 INFO RequestProcessor-5 xfd.DispenseHeadXpm - Head 1014349 row 1 had 8329 drops, row 2 had 8085 drops after rows were swapped.\n2015-09-02 10:00:05,465 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetPrintDataUpdated...call success\n2015-09-02 10:00:05,465 INFO RequestProcessor-5 xfd.printmanagerXPM - Loading swathe 1 of 1\n2015-09-02 10:00:05,465 INFO RequestProcessor-5 xfd.DispenseHeadXpm - loadBitmap:     = 128, colCount = 741, totalSize = 94848\n2015-09-02 10:00:05,466 INFO RequestProcessor-5 xfd.DispenseHeadXpm - XPMSEPDSetup: 3\n2015-09-02 10:00:05,469 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSelectSEPD...call success\n2015-09-02 10:00:05,472 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionReloadAppXMLFileParameters...call success\n2015-09-02 10:00:05,475 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling XaarScorpionGetMaxHeadBlocksXPM...call success\n2015-09-02 10:00:05,484 INFO RequestProcessor-5 xfd.XPM - XaarCmdAPI: Calling bXaarScorpionSetupImageDataParametersUpdated...call success\n2015-09-02 10:00:05,494 INFO RequestProcessor-5 xfd.DispenseHeadXpm - Head 1014349 row 1 had 8085 drops, row 2 had 8085 drops after rows were swapped."

    re.findall(p, test_str)
    '''

    multipass_pattern=ur'Vector 1 is.*?\r\n201[56]-..-..\ (?P<start1_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.xfdservice - Dispensing pattern for tcs:. recipe:. swathe:0.*?\r\n201[56]-..-..\ (?P<end1_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\r\n201[56]-..-..\ (?P<start2_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.xfdservice - Dispensing pattern for tcs:. recipe:. swathe:1.*?\r\n201[56]-..-..\ (?P<fake_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.XPM - XaarCmdAPI: Calling bXaarScorpionEnablePrintMode...call success\r\n201[56]-..-..\ (?P<end2_ts>[0-9:,]*)\ INFO RequestProcessor-. xfd.XPM - XaarCmdAPI: Calling bXaarScorpionXUSBBusy...call success\r\n'

    f = open(xfdLog, 'r')
    buf = f.read()
    f.close()
    print "File (%s) opened and read into buffer, length of buf: %d" % (xfdLog, len(buf))

    #XUSBBusy_sets = [x.groupdict() for x in re.finditer(XUSBBusy_pattern, buf, re.DOTALL)]
    multipass_sets = [x.groupdict() for x in re.finditer(multipass_pattern, buf, re.DOTALL)]
    print "Parsing log for multipass calls...found %d records." % (len(multipass_sets))
    if len(multipass_sets) > 0: print " >> Date range: %s - %s" % (multipass_sets[0]['start1_ts'], multipass_sets[-1]['start1_ts'])

    timestamp_format = "%H:%M:%S,%f"

    processing_times_pass1 = []
    processing_times_pass2 = []
    processing_times_multipass = []
    for multipass_set in multipass_sets:
        '''
        [{u'end_ts': u'20:24:02,481', u'start_ts': u'20:24:02,442'},
         {u'end_ts': u'20:24:02,620', u'start_ts': u'20:24:02,514'},
         {u'end_ts': u'20:24:02,629', u'start_ts': u'20:24:02,622'},
         {u'end_ts': u'20:34:02,483', u'start_ts': u'20:34:02,442'},
         {u'end_ts': u'20:34:02,622', u'start_ts': u'20:34:02,516'},
         {u'end_ts': u'20:34:02,631', u'start_ts': u'20:34:02,624'}]
        '''
        start1_ts = dt.datetime.strptime(multipass_set['start1_ts'], timestamp_format)
        end1_ts   = dt.datetime.strptime(multipass_set['end1_ts'], timestamp_format)
        start2_ts = dt.datetime.strptime(multipass_set['start2_ts'], timestamp_format)
        end2_ts   = dt.datetime.strptime(multipass_set['end2_ts'], timestamp_format)
        pass1_delta = end1_ts-start1_ts
        delta1_ms = pass1_delta.total_seconds() * 1000
        pass2_delta = end2_ts-start2_ts
        delta2_ms = pass2_delta.total_seconds() * 1000
        processing_times_multipass.append(delta1_ms+delta2_ms)
        processing_times_pass1.append(delta1_ms)
        processing_times_pass2.append(delta2_ms)

    processing_times_pass1_np = np.array(processing_times_pass1)
    processing_times_pass2_np = np.array(processing_times_pass2)
    processing_times_multipass_np = np.array(processing_times_multipass)

    if len(processing_times_multipass) == 0:
        return

    fig = plt.figure(figsize=(10*2,5))
    ax = fig.add_subplot(111)
    ax.set_title('MultiPass XFD Processing time - Non-Optimized')
    ax.set_ylabel('time (ms)')
    ax.text(0.55, 0.75, ("mean=%.f" % (np.round(processing_times_multipass_np.mean()))),
        horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
    ax.text(0.55, 0.70, ("stdev=%.2f" % (processing_times_multipass_np.std())),
        horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
    ax.text(0.55, 0.65, ("max=%.2f" % (processing_times_multipass_np.max())),
        horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
    ax.text(0.55, 0.60, ("min=%.2f" % (processing_times_multipass_np.min())),
        horizontalalignment='left',verticalalignment='bottom',transform=ax.transAxes)
    ax.hlines(processing_times_multipass_np.mean(), 0, len(processing_times_multipass), color='r', linewidth=2, linestyle='--')
    ax.plot(processing_times_multipass, color='b', label='Total', linewidth=2)
    ax.plot(processing_times_pass1, color='g', label='Pass1')
    ax.plot(processing_times_pass2, color='c', label='Pass2')
    ax.legend()
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
