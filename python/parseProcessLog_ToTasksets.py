#!/usr/bin/env python

import sys
import time
import re
import argparse
import json
import numpy as np
from collections import defaultdict
from collections import OrderedDict

import taskset_ids as ts

def parseProcessLog(processLog, output_path, start_date='', end_date='', generic=False):

    drink_metric_sets_pattern = r'''
        ProcessMetrics\ -\ Start:.*?
        ProcessID:\ (?P<process_id>[0-9]*)            # ProcessID
        .*?DrinkID:\ (?P<drink_id>[0-9]*)             # drinkID
        .*?Tasksets:\ (?P<tasksets_raw>.*?)           # tasksets
        Queued:\ (?P<queued_time>[0-9.]*)             # queued time
        .*?Processing:\ (?P<processing_time>[0-9.]*)  # processing time
        .*?ProcessMetrics\ -\ End:
        '''

    taskset_pattern = r'''
        For\ taskset\ ID:\ (?P<taskset_id>[0-9]*)  # tasksetID
        .*?Transport:\ (?P<trans_time>[0-9.]*),    # transport time
        \ Resource:\ (?P<res_time>[0-9.]*)         # Resource time
        .*?activity:\ (?P<activity_time>[0-9.]*),  # activity time
        \ slack:\ (?P<slack_time>[0-9.]*)          # slack time
        '''

    PID_Row_pattern = r'''
        :\ PID:(?P<process_id>[0-9]*)           # ProcessID
        .*?,\ Row:(?P<row_id>[0-9])             # row
        '''

    f = open(processLog, 'r')

    #
    # Use start_date and (possibly) end_date to limit the amount
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

    end_offset = 0
    if end_date:
        f.seek(0)
        match = re.search(end_date, f.read())
        if match:
            end_offset = match.span()[0]
            if end_offset > start_offset:
                print "End date found...truncating at byte offset %d" % (end_offset)
            else:
                print "End date found, but its before start date.  No truncating..."
                end_offset = 0
        else:
            print "!! End date NOT found...reading to end of log"
            end_offset = 0

    f.seek(start_offset)
    if end_offset > start_offset:
        buf = f.read(end_offset - start_offset)
    else:
        buf = f.read()
    f.close()
    print "start_offset = %d, end_offset = %d, length of buf: %d" % (start_offset, end_offset, len(buf))

    drink_metric_sets = [x.groupdict() for x in re.finditer(drink_metric_sets_pattern, buf, re.DOTALL|re.X)]
    #PID_Row_sets      = [x.groupdict() for x in re.finditer(PID_Row_pattern, buf, re.X)]

    drink_stats_list = []
    tasksetGroup_stats = {} 
    taskset_stats = {} 

    if generic:
        print "Treating esp and froth resources as generic locations"

    for idx, drink_metric_set in enumerate(drink_metric_sets):
        drink_metric_set['taskset_metrics'] = [x.groupdict() for x in re.finditer(taskset_pattern, drink_metric_set['tasksets_raw'], re.DOTALL|re.X)]

        drink_stats = {}
        drink_stats['taskset_ids'] = []
        drink_stats['processing_time'] = drink_metric_set['processing_time']
        drink_stats['queued_time']     = drink_metric_set['queued_time']
        drink_stats['drink_id']        = drink_metric_set['drink_id']

        tasksetGroup = []

        for taskset_metric in drink_metric_set['taskset_metrics']:

            taskset_id = taskset_metric['taskset_id']
            tasksetGroup.append(int(taskset_id))

            ts_id_dict = dict({taskset_id: ts.stringifyTasksetID(int(taskset_id), False)})
            drink_stats['taskset_ids'].append(ts_id_dict)

            if taskset_id not in taskset_stats:
                taskset_stats[taskset_id] = {}
                taskset_stats[taskset_id]['activity_time'] = {}
                taskset_stats[taskset_id]['activity_time']['raw'] = []
                taskset_stats[taskset_id]['res_time'] = {}
                taskset_stats[taskset_id]['res_time']['raw'] = []
                taskset_stats[taskset_id]['slack_time'] = {}
                taskset_stats[taskset_id]['slack_time']['raw'] = []
                taskset_stats[taskset_id]['trans_time'] = {}
                taskset_stats[taskset_id]['trans_time']['raw'] = []
            taskset_stats[taskset_id]['activity_time']['raw'].append(float(taskset_metric['activity_time']))
            taskset_stats[taskset_id]['res_time']['raw'].append(float(taskset_metric['res_time']))
            taskset_stats[taskset_id]['slack_time']['raw'].append(float(taskset_metric['slack_time']))
            taskset_stats[taskset_id]['trans_time']['raw'].append(float(taskset_metric['trans_time']))
            
        drink_stats_list.append(drink_stats)

        tasksetGroupID = str(ts.encodeTasksetGroup(tasksetGroup, generic=generic))
        if tasksetGroupID not in tasksetGroup_stats:
            tasksetGroup_stats[tasksetGroupID] = {}
            tasksetGroup_stats[tasksetGroupID]['tasksetGroup'] = tasksetGroup
            tasksetGroup_stats[tasksetGroupID]['info'] = ts.stringifyTasksetGroup(tasksetGroup, generic=generic)
            tasksetGroup_stats[tasksetGroupID]['processing_time'] = {}
            tasksetGroup_stats[tasksetGroupID]['processing_time']['raw'] = []
            tasksetGroup_stats[tasksetGroupID]['queued_time'] = {}
            tasksetGroup_stats[tasksetGroupID]['queued_time']['raw'] = []
        tasksetGroup_stats[tasksetGroupID]['processing_time']['raw'].append(float(drink_stats['processing_time']))
        tasksetGroup_stats[tasksetGroupID]['queued_time']['raw'].append(float(drink_stats['queued_time']))

    print "Parsing complete.  Found %d drink metrics" % (len(drink_metric_sets))
    print "Now doing statistics on raw taskset stats..."

    for taskset_id in taskset_stats.keys():
        taskset_stats[taskset_id]['info'] = ts.stringifyTasksetID(int(taskset_id), False)

        activity_time_np = np.array(taskset_stats[taskset_id]['activity_time']['raw'])
        taskset_stats[taskset_id]['activity_time']['max']  = activity_time_np.max()
        taskset_stats[taskset_id]['activity_time']['min']  = activity_time_np.min()
        taskset_stats[taskset_id]['activity_time']['mean'] = activity_time_np.mean()
        taskset_stats[taskset_id]['activity_time']['std']  = activity_time_np.std()
        taskset_stats[taskset_id]['activity_time']['n']    = activity_time_np.size
        del taskset_stats[taskset_id]['activity_time']['raw']
        
        res_time_np = np.array(taskset_stats[taskset_id]['res_time']['raw'])
        taskset_stats[taskset_id]['res_time']['max']  = res_time_np.max()
        taskset_stats[taskset_id]['res_time']['min']  = res_time_np.min()
        taskset_stats[taskset_id]['res_time']['mean'] = res_time_np.mean()
        taskset_stats[taskset_id]['res_time']['std']  = res_time_np.std()
        taskset_stats[taskset_id]['res_time']['n']    = res_time_np.size
        del taskset_stats[taskset_id]['res_time']['raw']
        
        slack_time_np = np.array(taskset_stats[taskset_id]['slack_time']['raw'])
        taskset_stats[taskset_id]['slack_time']['max']  = slack_time_np.max()
        taskset_stats[taskset_id]['slack_time']['min']  = slack_time_np.min()
        taskset_stats[taskset_id]['slack_time']['mean'] = slack_time_np.mean()
        taskset_stats[taskset_id]['slack_time']['std']  = slack_time_np.std()
        taskset_stats[taskset_id]['slack_time']['n']    = slack_time_np.size
        del taskset_stats[taskset_id]['slack_time']['raw']
        
        trans_time_np = np.array(taskset_stats[taskset_id]['trans_time']['raw'])
        taskset_stats[taskset_id]['trans_time']['max']  = trans_time_np.max()
        taskset_stats[taskset_id]['trans_time']['min']  = trans_time_np.min()
        taskset_stats[taskset_id]['trans_time']['mean'] = trans_time_np.mean()
        taskset_stats[taskset_id]['trans_time']['std']  = trans_time_np.std()
        taskset_stats[taskset_id]['trans_time']['n']    = trans_time_np.size
        del taskset_stats[taskset_id]['trans_time']['raw']

    short_list = []
    plot_data_list = []
    for tasksetGroupID in tasksetGroup_stats.keys():
        processing_time_np = np.array(tasksetGroup_stats[tasksetGroupID]['processing_time']['raw'])
        tasksetGroup_stats[tasksetGroupID]['processing_time']['max']  = processing_time_np.max()
        tasksetGroup_stats[tasksetGroupID]['processing_time']['min']  = processing_time_np.min()
        tasksetGroup_stats[tasksetGroupID]['processing_time']['mean'] = processing_time_np.mean()
        tasksetGroup_stats[tasksetGroupID]['processing_time']['std']  = processing_time_np.std()
        tasksetGroup_stats[tasksetGroupID]['processing_time']['n']    = processing_time_np.size
        del tasksetGroup_stats[tasksetGroupID]['processing_time']['raw']

        queued_time_np = np.array(tasksetGroup_stats[tasksetGroupID]['queued_time']['raw'])
        tasksetGroup_stats[tasksetGroupID]['queued_time']['max']  = queued_time_np.max()
        tasksetGroup_stats[tasksetGroupID]['queued_time']['min']  = queued_time_np.min()
        tasksetGroup_stats[tasksetGroupID]['queued_time']['mean'] = queued_time_np.mean()
        tasksetGroup_stats[tasksetGroupID]['queued_time']['std']  = queued_time_np.std()
        tasksetGroup_stats[tasksetGroupID]['queued_time']['n']    = queued_time_np.size
        del tasksetGroup_stats[tasksetGroupID]['queued_time']['raw']

        short_list.append("%s, num: %d, mean_time: %d (%s:[%s])" % 
            (tasksetGroup_stats[tasksetGroupID]['info'], processing_time_np.size, processing_time_np.mean(), 
            tasksetGroupID, ', '.join(str(e) for e in tasksetGroup_stats[tasksetGroupID]['tasksetGroup'])))

        plot_data = {}
        plot_data['TasksetGroupID'] = tasksetGroupID
        plot_data['info'] = tasksetGroup_stats[tasksetGroupID]['info']
        plot_data['queued_time_mean'] = tasksetGroup_stats[tasksetGroupID]['queued_time']['mean']
        plot_data['processing_time_mean'] = tasksetGroup_stats[tasksetGroupID]['processing_time']['mean']
        plot_data['n1'] = tasksetGroup_stats[tasksetGroupID]['processing_time']['n']

        activity_time_mean, res_time_mean, slack_time_mean, trans_time_mean = 0.0, 0.0, 0.0, 0.0

        for tasksetID in tasksetGroup_stats[tasksetGroupID]['tasksetGroup']:
            taskset_stat = taskset_stats[str(tasksetID)]
            activity_time_mean += taskset_stat['activity_time']['mean']
            res_time_mean      += taskset_stat['res_time']['mean']
            slack_time_mean    += taskset_stat['slack_time']['mean']
            trans_time_mean    += taskset_stat['trans_time']['mean']
        plot_data['n2'] = taskset_stat['trans_time']['n']

        plot_data['processing_time_calc'] = res_time_mean + trans_time_mean
        plot_data['activity_time_mean'] = activity_time_mean
        plot_data['res_time_mean'] = res_time_mean
        plot_data['slack_time_mean'] = slack_time_mean
        plot_data['trans_time_mean'] = trans_time_mean
        plot_data['num_tasksets'] = len(tasksetGroup_stats[tasksetGroupID]['tasksetGroup'])

        # break up the info str to get extra data for plotting...hack!
        # Denest->Esp->WIP, urn/h20: N, ice: N, lid: Y, NFADDs: 0, RFADDs: 1"
        #
        info_list = tasksetGroup_stats[tasksetGroupID]['info'].split(',')
        plot_data['locs']    = info_list[0]
        plot_data['urn_h20'] = (1 if info_list[1].split(':')[1].strip() == 'Y' else 0)
        plot_data['ice']     = (1 if info_list[2].split(':')[1].strip() == 'Y' else 0)
        plot_data['lid']     = (1 if info_list[3].split(':')[1].strip() == 'Y' else 0)
        plot_data['NFADDs']  = int(info_list[4].split(':')[1].strip())
        plot_data['RFADDs']  = int(info_list[5].split(':')[1].strip())

        plot_data_list.append(plot_data)

    print "Calculated stats on %d taskset IDs" % (len(taskset_stats.keys()))

    fout = open(('%s/taskset_ids.json' % (output_path)), 'w')
    fout.write(json.dumps(taskset_stats, sort_keys=True, indent=4, separators=(',', ': ')))
    fout.close()

    fout = open(('%s/drink_stats.json' % (output_path)), 'w')
    fout.write(json.dumps(drink_stats_list, sort_keys=True, indent=4, separators=(',', ': ')))
    fout.close()

    fout = open(('%s/tasksetGroup_stats.json' % (output_path)), 'w')
    fout.write(json.dumps(tasksetGroup_stats, sort_keys=True, indent=4, separators=(',', ': ')))
    fout.close()

    short_list.sort()
    fout = open(('%s/short_list.json' % (output_path)), 'w')
    fout.write(json.dumps(short_list, sort_keys=True, indent=4, separators=(',', ': ')))
    fout.close()

    fout = open(('%s/plot_data.json' % (output_path)), 'w')
    fout.write(json.dumps(plot_data_list, sort_keys=True, indent=4, separators=(',', ': ')))
    fout.close()

if __name__ == "__main__":
    '''
    parseProcessLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-i', '--in_file', dest='in_file', type=str,
                        help='input file...if not specified then use stdin')
    parser.add_argument('-o', '--output_path', dest='output_path', type=str,
                        help='output path...if not specified then will use /tmp', default='/tmp')
    parser.add_argument('-s', '--start_date', dest='start_date', type=str,
                        help='(optional) date to start parsing in the form of mm/dd/yyyy', default='')
    parser.add_argument('-e', '--end_date', dest='end_date', type=str,
                        help='(optional) date to end parsing in the form of mm/dd/yyyy', default='')
    parser.add_argument('-g', '--generic', dest='generic', action='store_true',
                        help='(optional) process the esp and frother resources as generic', default=False)

    args = parser.parse_args()

    if args.in_file:
        parseProcessLog(args.in_file, args.output_path, args.start_date, args.end_date, args.generic)
    else:
        parser.print_help()
        sys.exit(1)

