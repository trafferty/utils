#!/usr/bin/env python

import argparse
import re
import matplotlib.pyplot as plt
import numpy as np

def parse_disp_data(disp_log_file, start_date):

    '''
   Dispense Steps: 8/7/2014 4:26:15 PM: START_STEP_DUMP [96000821]
   DISP_PUMP_SETUP:  ->DISP_PUMP_START
   DISP_PUMP_SETUP: SendCmd: 27 0 4 15 0 25 0 2 ->DISP_PUMP_WAIT
   DISP_PUMP_VERIFY: Dispense complete! [CupWeight > (Initial + Target)]: 35.8 > 35.1
   >>>>> [96000821] DISP_PUMP_DONE: CupWeight: 37.4, Dispensed: 15.9, Target: 13.5, Delta: 2.4, TotalTime: 0, Attempts: 1 END_STEP_DUMP
    '''

    dispense_steps_pattern = r'''
        Dispense\ Steps:\ (?P<date>[0-9/: APM]*)              # date
        .*?START_STEP_DUMP\ \[(?P<drink_id>[0-9]*)\]          # drinkID
        .*?Count:\ (?P<count>[0-9]*)                          # count
        .*?_DONE:\ CupWeight:\ (?P<cup_weight>[0-9.]*)        # cup weight          
        .*?,\ Dispensed:\ (?P<dispensed_amount>[0-9.]*)       # dispensed amount
        .*?,\ Target:\ (?P<target_amount>[0-9.]*)             # target amount
        .*?,\ Delta:\ (?P<delta>[0-9.-]*)                     # delta
        .*?,\ TotalTime:\ (?P<total_time>[0-9]*)              # total time
        .*?,\ Attempts:\ (?P<attempts>[0-9]*)                 # attempts
        .*?END_STEP_DUMP
        '''

    f = open(disp_log_file, 'r')

    #
    # Use start_date to limit the amount
    # of the log that we parse
    #
    start_offset = 0
    if start_date:
        match = re.search(start_date, f.read())
        if match:
            start_offset = match.span()[0]
            print "Startdate found...seeking to byte offset %d" % (start_offset)
        else:
            print "!! Startdate NOT found...reading from beginning of log"

    f.seek(start_offset)
    buf = f.read()
    f.close()
    print "start_offset = %d, length of buf: %d.  parsing..." % (start_offset, len(buf))

    dispense_metrics = [x.groupdict() for x in re.finditer(dispense_steps_pattern, buf, re.DOTALL|re.X)]

    print "Parsing complete. %d metric sets found." % (len(dispense_metrics))
    return dispense_metrics


def plot_disp_metrics(dispense_metrics):
    deltas = []
    dispensed = []
    targets = []
    dates = []
    for metric in dispense_metrics:
        try:
            delta = float(metric['delta'])
            dispensed_amount = float(metric['dispensed_amount'])
            target_amount = float(metric['target_amount'])
            date = metric['date'].split(' ')[0]
        except ValueError:
            continue
        deltas.append(delta)
        dispensed.append(dispensed_amount)
        targets.append(target_amount)
        dates.append(date)

    fig, ax = plt.subplots()
    if 1:
        t = range(0, len(deltas))
        plt.plot(t, dispensed, t, targets, t, deltas)
        plt.xlabel("Dispense Operations.  Max Delta: %d, Min Delta %d, Mean Delta: %1.1f" % (np.max(deltas), np.min(deltas), np.mean(deltas)))
        plt.ylabel('grams')
        plt.legend(['Dispensed amount', 'Target amount', 'Delta'], loc = 'upper right')
        ax.set_ylim(min(deltas) - 20, max(max(dispensed), max(targets)) + 20)
        #plt.annotate('Data gathering drinks', xy=(5,150))
        #plt.annotate('MC tweaks to parms', xy=(14,150))
        #plt.annotate('restart MC', xy=(31,150))
        #plt.annotate('restart MC', xy=(39,150))

        #for idx, delta in enumerate(deltas):
            #plt.annotate('%2.1fg' % delta, xy=(idx, delta))
    else:

        index = np.arange(len(deltas))
        bar_width = 0.25
        opacity = 0.4

        rects1 = plt.bar(index, dispensed, bar_width,
                         alpha=opacity,
                         color='r',
                         label='Actual Amount')

        rects2 = plt.bar(index + bar_width, targets, bar_width,
                         alpha=opacity,
                         color='b',
                         label='Target Amount')

        plt.xlabel('Dispense Operations')
        plt.ylabel('grams')
        plt.title('Dispense operations: Target vs Actual')
        #plt.xticks(index + bar_width, ('A', 'B', 'C', 'D', 'E'))
        plt.legend()
        #plt.tight_layout()
        yloc = max(max(targets), max(dispensed)) 
        for idx, delta in enumerate(deltas):
            plt.annotate('%2.1fg' % delta, xy=(idx, dispensed[idx]))

    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse out dispense metric data from an MC-produced log')
    parser.add_argument('-d', '--disp_log_file', type=str, default="", help='log file with raw disp data in it')
    parser.add_argument('-s', '--start_date', dest='start_date', type=str,
                        help='(optional) date to start parsing in the form of mm/dd/yyyy', default='')
    args = parser.parse_args()

    if len(args.disp_log_file):
        dispense_metrics = parse_disp_data(args.disp_log_file, args.start_date)
        plot_disp_metrics(dispense_metrics)
    else:  
        print "Must specify file name for disp log"
