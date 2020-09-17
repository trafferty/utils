#!/usr/bin/python

import time
from datetime import datetime
import argparse
import RPi.GPIO as io
import socket
import signal

def doLog(log_msg):
    print("%s: %s" % (datetime.now().strftime("%Y_%d_%m (%a) - %H:%M:%S.%f")[:-3], log_msg))

if __name__ == "__main__":
    done = False
    def sigint_handler(signal, frame):
        global done
        print( "\nShutting down...")
        done = True
    signal.signal(signal.SIGINT, sigint_handler)
    
    parser = argparse.ArgumentParser(description='open socket on specified port, listen for "go", produce PD signal')
    parser.add_argument('-p',  dest='port', type=int, default=8888, help='port to listen on')
    parser.add_argument('-a',  dest='addr', type=str, default='', help='address to listen on')

    args = parser.parse_args()
    port = args.port
    addr = args.addr

    trigger_pin = 17
    LED_pin = 4
    pulse_time_s = 0.001

    io.setmode(io.BCM)
    io.setwarnings(False)

    io.setup(trigger_pin, io.OUT)
    io.setup(LED_pin, io.OUT)
    io.output(trigger_pin, io.LOW)
    io.output(LED_pin, io.LOW)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((addr, port))
    s.listen(10)
    doLog('Waiting on addr:port %s:%d' % (addr,port))
    conn, addr_conn = s.accept()
    doLog('Recieved conn from %s' % (addr_conn[0]))

    cnt = 0
    prev_ts = time.time()
    while not done:
        d = conn.recv(5)
        recv_ts = time.time()
        if d[0:2] == 'go':
            cnt += 1
            delta = recv_ts - prev_ts
            prev_ts = recv_ts
            doLog("Rcv'd go! cnt: %d, delta: %0.3f" % (cnt, delta))
            io.output(trigger_pin, io.HIGH)
            io.output(LED_pin, io.HIGH)
            time.sleep(pulse_time_s)
            io.output(trigger_pin, io.LOW)
            io.output(LED_pin, io.LOW)
        elif d[0:1] == 'q':
            break

    io.cleanup()
    s.close()