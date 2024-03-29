#!/usr/bin/python

import time
import sys
from datetime import datetime
import argparse
from labjack import ljm
import socket
import signal

from threaded_tcp_server import ThreadedTCPServer, SocketRequestHandler

LOW,HIGH = 0,1

def doLog(log_msg):
    print("%s: %s" % (datetime.now().strftime("%Y_%d_%m (%a) - %H:%M:%S.%f")[:-3], log_msg))


if __name__ == "__main__":
    done = False
    def sigint_handler(signal, frame):
        global done
        doLog( "\nShutting down...")
        done = True
    signal.signal(signal.SIGINT, sigint_handler)
    
    parser = argparse.ArgumentParser(description='open socket on specified port, listen for "go", produce PD signal')
    parser.add_argument('-p',  dest='port', type=int, default=8888, help='port to listen on')
    parser.add_argument('-a',  dest='addr', type=str, default='', help='address to listen on')

    args = parser.parse_args()
    port = args.port
    addr = args.addr

    handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
    if handle is None:
        doLog("Could not connect to LabJack. Connected?")
        sys.exit()

    info = ljm.getHandleInfo(handle)
    doLog("Opened a LabJack with Device type: %i, Connection type: %i,\n"
          "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
          (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    deviceType = info[0]

    # Setting FIO4 and 05 on the LabJack T4. FIO0-FIO3 are reserved for AIN0-AIN3.
    trigger_name = "FIO5"
    LED_name = "FIO4"

    # Reading from the digital line in case it was previously an analog input.
    ljm.eReadName(handle, trigger_name)
    ljm.eReadName(handle, LED_name)

    pulse_time_s = 0.001

    server = ThreadedTCPServer("LJ_server", (addr, port), SocketRequestHandler)
    #server.setCallback(test_callback_func)
    # Start the server...
    server.start();

    doLog("Server started on %s:%d.\nStarting process loop..." % (addr, port))
    cnt = 0
    prev_ts = time.time()
    while not done:
        input_line = server.input_fifo.get()
        if len(input_line) > 0:
            recv_ts = time.time()
            if input_line[0:2] == 'go':
                # pulse the trigger and LED DOs high then low
                ljm.eWriteName(handle, trigger_name, HIGH)
                ljm.eWriteName(handle, LED_name, HIGH)
                time.sleep(pulse_time_s)
                ljm.eWriteName(handle, trigger_name, LOW)
                ljm.eWriteName(handle, LED_name, LOW)
                # accounting...
                cnt += 1
                delta = recv_ts - prev_ts
                prev_ts = recv_ts
                doLog("Rcv'd go! cnt: %d, delta: %0.3f" % (cnt, delta))
            elif input_line[0:1] == 'q':
                break

    doLog("rec'd quit cmd, stopping loop...")

    server.stop()
    doLog("all shut down...")

    ljm.close(handle)
