import os
import fnmatch
import json
from dateutil import tz
from datetime import datetime
import operator
import argparse

def locate(pattern, root_path):
    for path, dirs, files in os.walk(os.path.abspath(root_path)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

def parseLogs(log_file):

    data = json.load(open(log_file, 'r'))

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    motion_count_by_hour = {}
    door_open_count_by_hour = {}
    for idx in range(1,25):
        motion_count_by_hour[idx] = door_open_count_by_hour[idx] = 0

    '''
    {u'door_status': u'0',
     u'motion_detected': u'1',
     u'timestamp': u'2014-08-05T12:13:26.977Z'}
     '''
    door_status = 0
    for d in data:
        if d['motion_detected'] == '1':
            utc_ts = datetime.strptime(d['timestamp'][0:-5], '%Y-%m-%dT%H:%M:%S')
            utc_ts = utc_ts.replace(tzinfo=from_zone)
            local_ts = utc_ts.astimezone(to_zone)
            motion_count_by_hour[local_ts.hour] += 1
        if d['door_status'] == '1' and door_status == 0:
            door_status = 1
            if d['motion_detected'] == '0':
                utc_ts = datetime.strptime(d['timestamp'][0:-5], '%Y-%m-%dT%H:%M:%S')
                utc_ts = utc_ts.replace(tzinfo=from_zone)
                local_ts = utc_ts.astimezone(to_zone)
            door_open_count_by_hour[local_ts.hour] += 1
        else:
            door_status = 0

    print("Data for range %s - %s\n----------------------------------------------------------" % 
        (data[-1]['timestamp'][0:-5],data[0]['timestamp'][0:-5]))
    max_motions    = float(max(motion_count_by_hour.iteritems(), key=operator.itemgetter(1))[1])
    max_door_opens = float(max(door_open_count_by_hour.iteritems(), key=operator.itemgetter(1))[1])
    max_val = max(max_motions, max_door_opens)
    val_width = len(str(int(max_val)))
    plot_width = 70
    hours = range(5,25) + range(1,5)
    for idx in hours:
        motions    = '#' * (0 if motion_count_by_hour[idx] == 0 else (int(motion_count_by_hour[idx]/max_val * (plot_width-1)) + 1))
        door_opens = '*' * (0 if door_open_count_by_hour[idx] == 0 else (int(door_open_count_by_hour[idx]/max_val * (plot_width-1)) + 1))
        am_pm = ('am' if idx < 12 else 'pm')
        hour  = (idx if idx <= 12 else idx-12)
        print("%2d%s motions   : %*d %s" % (hour, am_pm, val_width, motion_count_by_hour[idx], motions))
        print("%2d%s door opens: %*d %s" % (hour, am_pm, val_width, door_open_count_by_hour[idx], door_opens))
    total_motions = 0
    total_door_opens = 0
    print("----------------------------------------------------------" ) 
    print("Total motions   : %d" % sum(motion_count_by_hour.values()))
    print("Total door opens: %d" % sum(door_open_count_by_hour.values()))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Open and parse json log from garage door activity')
    parser.add_argument('-i', '--in_file', dest='in_file', type=str,
                        help='input file...if not specified then use stdin')
    args = parser.parse_args()

    if args.in_file:
        parseLogs(args.in_file)
    else:
        parser.print_help()
        sys.exit(1)
