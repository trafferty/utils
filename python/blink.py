#!/usr/bin/python

import time
import argparse
import CHIP_IO.GPIO as GPIO

def cycle(n, f):
    t = (1.0/f) / 2.0
    GPIO.output("CSID0", 0)
    for x in range(n+1):
        GPIO.output("CSID0", 1)
        time.sleep(t)
        GPIO.output("CSID0", 0)
        time.sleep(t)

if __name__ == "__main__":
    '''
    parseDIFLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-n',  dest='num_cycles', type=int, help='number of cycles')
    parser.add_argument('-f',  dest='freq', type=int, help='frequency in Hz')

    args = parser.parse_args()

    GPIO.setup("CSID0", GPIO.OUT)
    blink(100, 0.1)


