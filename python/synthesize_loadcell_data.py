#!/usr/bin/env python
import signal
import sys
import time
import argparse
import random
import numpy as np
import random

if __name__ == "__main__":
    '''
    synthesize_loadcell_data.py -r rate
    '''
    parser = argparse.ArgumentParser(description='Create synthesized loadcell data, either random or sinusoidal, output to either file or stdout')
    parser.add_argument('-o', dest='out_file', type=str, help='output file...if not specified then use stdout')
    parser.add_argument('-r', dest='rate', type=int, help='Rate for synthesized data stream (Hz) (default: 50)', default=50)
    parser.add_argument('-m', dest='median', type=int, help='Median value for data pt (default: 100)', default=100)
    parser.add_argument('-v', dest='variance', type=int, help='variance for synthesized data pts (default: 20)', default=20)
    parser.add_argument('-t', dest='test', action='store_true', help='no output, just print out the interpretation of the arguments')
    parser.add_argument('-s', dest='sine', action='store_true', help='instead of random data, produce a sine wave (default: off)')
    args = parser.parse_args()

    if args.out_file:
        outfile_name = args.out_file
        outFile = open(args.out_file, 'wb')
    else:
        outfile_name = 'stdout'
        outFile = sys.stdout

    sleep_time_ms = 1000/args.rate/1000.0
    data_terminator = ','

    if args.test:
        print 'rate: %d' % (args.rate)
        print 'median: %d' % (args.median)
        print 'variance: %d' % (args.variance)
        print 'sleep_time_ms: %f' % (sleep_time_ms)
        print 'test data pt: %s' % (str(args.median + random.randint(-20, 20)))
        print 'random or sine wave?: %s' % ('Sine wave' if args.sine else 'random')
        sys.exit()

    if args.sine:
        x=np.arange(0,2,0.05)
        y=(random.randint(5,args.variance))*np.sin(np.pi*x)
        idx = 0

    try:
        while True:
            if args.sine:
                data_pt = str(y[idx])
                idx += 1
                if idx == len(y):
                    y=(random.randint(5,args.variance))*np.sin(np.pi*x)
                    idx = 0
            else:
                data_pt = str(args.median + random.randint(-1 * args.variance, args.variance))
            outFile.write(data_pt)
            outFile.write(data_terminator)
            outFile.flush()
            time.sleep(sleep_time_ms)
    except KeyboardInterrupt:
        #print('\n\nProgram terminated from Ctrl+C!')
        sys.exit()