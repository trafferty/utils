#!/usr/bin/env python3
'''
Python app to capture process information

requires psutil:

  pip install psutil

Usage:

  ./capture_mem_percent.py -n process_name -w 1 -v | tee -a /tmp/mem_per_log
  
'''
import argparse
import time
import psutil

def find_pid(process_name):
    for pid in psutil.pids():
        if psutil.Process(pid).name() == process_name:
            return pid
    return -1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture process info')
    parser.add_argument('-n', '--process_name', type=str, help='name of the process', required=True)
    parser.add_argument('-w', '--wait_time_s', type=int, default=10, help='wait time in seconds (def=10s)', required=False)
    parser.add_argument('-v', dest='verbose', action='store_true', default=False)
    args = parser.parse_args()

    pid = find_pid(args.process_name)
    if pid >=0:
        p = psutil.Process(pid)
        while True:
            if args.verbose:
                print(("%s, %.6f, %.2f" %(time.strftime('%a %H:%M:%S'), p.memory_percent(), p.cpu_percent(interval=args.wait_time_s))), flush=True)
            else:
                print(("%.6f, %.2f" %(p.memory_percent(), p.cpu_percent(interval=args.wait_time_s))), flush=True)
