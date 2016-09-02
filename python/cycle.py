#!/usr/bin/python

import time
import argparse
import CHIP_IO.GPIO as GPIO

def cycle(l, n, f, w):
    t = (1.0/f)
    wait_adjusted = w - (n * t)
    print("Starting, %d loops.  f=%.2f, t=%f, n=%d, wait=%f, wait_adjusted=%f" % (l, f, t, n, w, wait_adjusted))
    GPIO.output("CSID0", 0)
    GPIO.output("CSID1", 0)
    for i in range(l):
        for x in range(n):
            GPIO.output("CSID0", 1)
            GPIO.output("CSID1", 1)
            time.sleep(t/2.0)
            GPIO.output("CSID0", 0)
            GPIO.output("CSID1", 0)
            time.sleep(t/2.0)
            print("  ...cycle complete: %d" % (x))
        print("...loop complete: %d" % (i))
        time.sleep(wait_adjusted)

if __name__ == "__main__":
    '''
    parseDIFLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-n',  dest='num_cycles', type=int, default=10, help='number of cycles')
    parser.add_argument('-l',  dest='loops', type=int, default=1, help='loops')
    parser.add_argument('-f',  dest='freq', type=float, default=1.0, help='frequency in Hz')
    parser.add_argument('-w',  dest='wait', type=float, default=1.0, help='wait time between loops')

    args = parser.parse_args()

    GPIO.setup("CSID0", GPIO.OUT)
    GPIO.setup("CSID1", GPIO.OUT)
    cycle(args.loops, args.num_cycles, args.freq, args.wait)
