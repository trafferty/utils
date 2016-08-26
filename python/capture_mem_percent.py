#!/usr/bin/env python3
'''
Python app to capture process information

requires psutil:

  pip install psutil

'''
import argparse
import signal
import time
import psutil

def find_pid(process_name):
    for pid in psutil.pids():
        if psutil.Process(pid).name() == process_name:
            return pid
    return -1

if __name__ == '__main__':
    done = False
    def sigint_handler(signal, frame):
        print( "\nCaught Ctrl-c...")
        done = True
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser(description='Capture process info')
    parser.add_argument('-n', '--process_name', type=str, help='name of the process', required=True)
    parser.add_argument('-w', '--wait_time_s', type=int, default=10, help='wait time in seconds (def=10s)', required=True)
    args = parser.parse_args()

    pid = find_pid(args.process_name)
    if pid >=0:
        p = psutil.Process(pid)
        while not done:
            memory_percent = p.memory_percent()
            print(memory_percent)
            time.sleep(args.wait_time_s)
