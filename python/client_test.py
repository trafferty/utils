#!/usr/bin/env python3

import time
import argparse
import json
from random import random, randint

# local modules
from client_socket import ClientSocket

done = False
def test_callback_func(msg):
    global done
    print("Rec'd: " + msg)
    if msg.find('quit') >= 0:
        print("Setting done == True")
        done = True

if __name__ == '__main__':
    global done
    parser = argparse.ArgumentParser(description='Client Socket class - Tester')
    parser.add_argument("port", type=int, help='Port on localhost to use')
    args = parser.parse_args()

    port = args.port if args.port else 12888

    c = ClientSocket('test', ('127.0.0.1', port), '')
    c.setCallback(test_callback_func)
    c.start()
    time.sleep(0.5)  # sleep a bit to allow reply

    start_ts = time.time()
    cnt = 0
    total_loops = 1000
    while not done:
        cnt = cnt+1 if cnt < total_loops else 1
        loop_update = {
            'LocX_mm': '%3.3f' % (randint(0, 500)+random()),
            'LocY_mm': '%3.3f' % (randint(0, 50)+random()),
            'Loop Count': str(cnt),
            'Run Mode': 'Recipe',
            'StageMoving': True,
            'Total Loops': str(total_loops),
            'Elapsed Time': '%5.3f' % (time.time() - start_ts), 
            'Mean Time per Loop': '%3.3f' % (randint(1, 2)+random()), 
            'Est Completion Time': '%s' % (time.strftime("%Y_%d_%m (%a) - %H:%M:%S", time.localtime())), 
            'Experiment Type': 'Test', 
            'Nozzle': '%d' % (randint(0,499)),
            'Row': '%d' % (randint(0,1)), 
            'Waveform': 'F3456_YHEEEE_HAAAAA.txt', 
            'Sample Clock': '%3.3f' % (randint(0, 30)+random()),
            'Global Voltage': '%3.3f' % (randint(16, 25)+random()),
            'PD_delay_us': '%d' % (randint(0, 10)*10) }
        msg = dict()
        msg['event'] = 'loop_update'
        msg['loop_update'] = loop_update
        c.write(json.dumps(msg))
        time.sleep(randint(0, 1)+random())
    c.stop()



