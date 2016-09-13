#!/usr/bin/python

import time
from datetime import datetime
import argparse
import CHIP_IO.GPIO as GPIO
import socket

def doLog(log_msg):
    print("%s: %s" % (datetime.now().strftime("%Y_%d_%m (%a) - %H:%M:%S.%f")[:-3], log_msg))

if __name__ == "__main__":
    '''
    pd_socketServer.py -p port
    '''
    parser = argparse.ArgumentParser(description='open socket on specified port, listen for "go", produce PD signal')
    parser.add_argument('-p',  dest='port', type=int, default=8888, help='port to listen on')

    args = parser.parse_args()

    GPIO.setup("CSID0", GPIO.OUT)
    GPIO.setup("CSID1", GPIO.OUT)
    GPIO.output("CSID0", 0)
    GPIO.output("CSID1", 0)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', args.port))
    s.listen(10)
    doLog('Waiting on port %d' % ( args.port))
    conn, addr = s.accept()
    #doLog('Recieved conn from %s' % (addr))
    doLog('Recieved conn...')

    while True:
        d = conn.recv(10)
        if d[0:2] == 'go':
            doLog("Rcv'd: %s" % (d[:-2]))
            GPIO.output("CSID0", 1)
            GPIO.output("CSID1", 1)
            time.sleep(0.100)
            GPIO.output("CSID0", 0)
            GPIO.output("CSID1", 0)

