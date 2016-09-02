#!/usr/bin/python

import time
import argparse
import CHIP_IO.GPIO as GPIO

def cycle(n, f):
    t = (1.0/f)
    print("Starting cycle.  f=%.2f, t=%f, n=%d" % (f, t, n))
    GPIO.output("CSID0", 0)
    for x in range(n+1):
        GPIO.output("CSID0", 1)
        GPIO.output("CSID1", 1)
        time.sleep(t/2.0)
        GPIO.output("CSID0", 0)
        GPIO.output("CSID1", 0)
        time.sleep(t/2.0)
        print("...cycle complete: %d" % (x))

if __name__ == "__main__":
    '''
    parseDIFLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-n',  dest='num_cycles', type=int, default=10, help='number of cycles')
    parser.add_argument('-f',  dest='freq', type=float, default=1.0, help='frequency in Hz')

    args = parser.parse_args()

    GPIO.setup("CSID0", GPIO.OUT)
    GPIO.setup("CSID1", GPIO.OUT)
    cycle(args.num_cycles, args.freq)
