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

def parseLog(log):
    '''
    '''
        
    regex_pattern=ur'] (?P<strategy>[A-Za-z]*) area \(mm2\): (?P<area>[0-9.]*), rad \(mm\): (?P<rad>[0-9.]*), cp \(x,y\): \((?P<cp_x>[0-9.-]*), (?P<cp_y>[0-9.-]*)\)'

    f = open(log, 'r')
    buf = f.read()
    f.close()
    print "File (%s) opened and read into buffer, length of buf: %d" % (log, len(buf))

    #regex_sets = [x.groupdict() for x in re.finditer(regex_pattern, buf, re.DOTALL)]
    regex_sets = [x.groupdict() for x in re.finditer(regex_pattern, buf)]
    print "Parsing log...found %d records." % (len(regex_sets))

    timestamp_format = "%H:%M:%S.%f"

    EdgeCircle_area = []
    EdgeCircle_rad = []
    EdgeCircle_cp_x = []
    EdgeCircle_cp_y = []
    BinaryDelta_area = []
    BinaryDelta_rad = []
    BinaryDelta_cp_x = []
    BinaryDelta_cp_y = []
    for regex_set in regex_sets:
        if regex_set['strategy'] == 'BinaryDelta':
            BinaryDelta_area.append(regex_set['area'])
            BinaryDelta_rad.append(regex_set['rad'])
            BinaryDelta_cp_x.append(regex_set['cp_x'])
            BinaryDelta_cp_y.append(regex_set['cp_y'])
        elif regex_set['strategy'] == 'EdgeCircles':
            EdgeCircle_area.append(regex_set['area'])
            EdgeCircle_rad.append(regex_set['rad'])
            EdgeCircle_cp_x.append(regex_set['cp_x'])
            EdgeCircle_cp_y.append(regex_set['cp_y'])

    if len(EdgeCircle_area) + len(BinaryDelta_area) == 0:
        return

    fig = plt.figure(figsize=(10*2,5))
    plt.plot(BinaryDelta_area, color='b', label='BinaryDelta Area')
    plt.plot(EdgeCircle_area, color='g', label='EdgeCircle Area')
    plt.ylabel('mm2')
    plt.title('Area: BinaryDelta vs EdgeCircle')
    plt.legend()

    fig = plt.figure(figsize=(10*2,5))
    plt.plot(BinaryDelta_rad, color='b', label='BinaryDelta Radius')
    plt.plot(EdgeCircle_rad, color='g', label='EdgeCircle Radius')
    plt.ylabel('mm')
    plt.title('Radius: BinaryDelta vs EdgeCircle')
    plt.legend()

    fig = plt.figure(figsize=(5,5))
    plt.plot(BinaryDelta_cp_x, BinaryDelta_cp_y, color='b', label='BinaryDelta CPs')
    plt.plot(EdgeCircle_cp_x, EdgeCircle_cp_y, color='g', label='EdgeCircle CPs')
    # plt.xticks([t for t in range(50, stats['image_dims'][1], 50)] )
    # plt.yticks([t for t in range(50, stats['image_dims'][0], 50)] )
    plt.title('Center Locs')
    plt.legend()
    #plt.savefig('../results/%s_CenterLocs.png' % (result_name))

    fig = plt.figure(figsize=(5,5))
    plt.scatter(BinaryDelta_cp_x, BinaryDelta_cp_y, color='b', label='BinaryDelta (n=%d)'%(len(BinaryDelta_cp_y)))
    plt.scatter(EdgeCircle_cp_x, EdgeCircle_cp_y, color='g', label='EdgeCircle (n=%d)'%(len(EdgeCircle_cp_y)))
    plt.xlabel('mm')
    plt.ylabel('mm')
    plt.title('Center Locs')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    '''
    parseLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-i', '--in_file', dest='in_file', type=str,
                        help='input file...if not specified then use stdin')

    args = parser.parse_args()

    if args.in_file:
        parseLog(args.in_file)
    else:
        parser.print_help()
        sys.exit(1)
