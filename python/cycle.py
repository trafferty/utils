#!/usr/bin/python

import time
from datetime import datetime
import argparse
import CHIP_IO.GPIO as GPIO

def doLog(log_msg):
    print("%s: %s" % (datetime.now().strftime("%Y_%d_%m (%a) - %H:%M:%S.%f")[:-3], log_msg))

def cycle(num_loops, loop_time_s, num_cycles, freq):
    time_between_cycles = (1.0/freq)
    doLog("Starting, %d loops.  freq=%.2f, time_between_cycles=%f, num_cycles=%d" % (num_loops, freq, time_between_cycles, num_cycles))
    GPIO.output("CSID0", 0)
    GPIO.output("CSID1", 0)
    for loop_cnt in range(num_loops):
        start_ts = time.time()
        for cycle_cnt in range(num_cycles):
            GPIO.output("CSID0", 1)
            GPIO.output("CSID1", 1)
            time.sleep(time_between_cycles/2.0)
            GPIO.output("CSID0", 0)
            GPIO.output("CSID1", 0)
            time.sleep(time_between_cycles/2.0)
            doLog("  ...cycle complete: %d" % (cycle_cnt))
        doLog("...loop complete: %d" % (loop_cnt))
        while ((time.time() - start_ts) < (loop_time_s-0.002)):
            time.sleep(0.004)

if __name__ == "__main__":
    '''
    parseDIFLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-c',  dest='num_cycles', type=int, default=10, help='number of cycles')
    parser.add_argument('-l',  dest='num_loops', type=int, default=1, help='loops')
    parser.add_argument('-f',  dest='freq', type=float, default=1.0, help='frequency in Hz')
    parser.add_argument('-t',  dest='loop_time_s', type=float, default=1.0, help='elapsed loop time')

    args = parser.parse_args()

    GPIO.setup("CSID0", GPIO.OUT)
    GPIO.setup("CSID1", GPIO.OUT)
    cycle(args.num_loops, args.loop_time_s, args.num_cycles, args.freq)
