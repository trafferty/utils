import sys
import time
import argparse
from collections import defaultdict
from collections import OrderedDict

STATE_ORDERED, STATE_COMPLETED, STATE_PICKUP, STATE_PRESENTED, STATE_CUSTOMER = range(5)

def getTimestamp(line):
    idx = line.find(':') + 2
    if idx < 0: 
        raise RuntimeError('Could not determine timestamp')
    idx2 = line.find('M: ', idx) + 1
    if idx2 < 0: 
        raise RuntimeError('Could not determine timestamp')
    date_str = line[ idx:idx2 ]
    time_stamp = time.mktime( time.strptime(date_str, format) )
    time_struct = time.gmtime(time_stamp)
    return time_stamp, time_struct

if __name__ == "__main__":
    '''
    parseLogFile.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open file, parse it according to parse function')
    parser.add_argument('-i', '--inFile', dest='inFile', type=str,
                        help='input file...if not specified then use stdin')
    parser.add_argument('-s', '--startDate', dest='startDate', type=str,
                        help='date to start parsing', default='')
    args = parser.parse_args()

    with open(args.inFile) as f:
        lines = f.readlines()
    f.close()

    format = "%m/%d/%Y %H:%M:%S %p"

    drink_data = defaultdict(dict)
    #drink_count = OrderedDict(list)
    drink_count = defaultdict(list)
    restarts = 0
    tm_yday = -1
    tm_hour = -1
    timestamp_min_max = [0, 0]

    current_hour = "0.0"

    for line in lines:
        # try:
        #     time_stamp, time_struct = getTimestamp(line)
        #     current_hour = "%d.%d" % (time_struct.tm_yday, time_struct.tm_hour)            
        #     if time_struct.tm_yday > tm_yday:
        #         tm_yday = time_struct.tm_yday
        #         print "New day detected: %s" % ( time.strftime(format, time_struct) )
        #     if time_struct.tm_hour > tm_hour:
        #         tm_hour = time_struct.tm_hour
        # except:
        #     #print "Caught exception..."
        #     continue

        #Order received : ID=26182 Name=Cappuccino
        if line.find('Order received : ID=') >= 0:
            line = line.rstrip('\r\n')

            try:
                time_stamp, time_struct = getTimestamp(line)
            except:
                #print "Caught exception..."
                continue

            if timestamp_min_max[0] == 0:
                timestamp_min_max[0] = time_struct
            timestamp_min_max[1] = time_struct

            drink_id = line[ line.find('ID=')+3 : line.rfind(' Name=') ]
            drink_type = line[ line.rfind('=')+1 :  ]
            # if drink_id in drink_data:
            #     restarts += 1
            #     restart = True
            # else:
            #     restart = False
            drink = {}
            drink['drink_id']   = drink_id
            drink['drink_type'] = drink_type
            drink['start_ts'] = time_stamp
            drink['start_time_struct'] = time_struct
            drink['restart'] = True if drink_id in drink_data else False
            drink['state'] = STATE_ORDERED
            drink_data[drink_id] = drink

            # ts_lst = []
            # ts_lst.append(time_stamp)
            # drink_data[drink_id] = ts_lst
            #print "New drink.  Id: %s, type: %s" % (drink_id, drink_type)

        elif line.find('Drink order completed') >= 0:
            try:
                time_stamp, time_struct = getTimestamp(line)
            except:
                #print "Caught exception..."
                continue
            drink_id = line[ line.rfind(':')+2 : line.rfind('.') ]
            if drink_id in drink_data:
                drink_data[drink_id]['complete_ts'] = time_stamp
                drink_data[drink_id]['state'] = STATE_COMPLETED

                # delta = drink_data[drink_id][1] - drink_data[drink_id][0]
                # drink_data[drink_id].append(delta)

                if current_hour not in drink_count:
                    count_lst = []                         # create a list
                    count_lst.append(1)                    # put a cnt value in
                    count_lst.append(time_struct)          # put the current time struct in
                    drink_count[current_hour] = count_lst  # assign the list
                else:
                    drink_count[current_hour][0] += 1
                    drink_count[current_hour][1] = time_struct
            else:
                print "Drink id: %s not found...skipping" % (drink_id)
        elif line.find('OrderManager: Pickup command received, DrinkID') >= 0:
            try:
                time_stamp, time_struct = getTimestamp(line)
            except:
                #print "Caught exception..."
                continue
            drink_id = line[ line.rfind('[')+1 : line.rfind(']') ]
            if drink_id in drink_data:
                drink_data[drink_id]['pickup_cmd_ts'] = time_stamp
                drink_data[drink_id]['state'] = STATE_PICKUP

            else:
                print "Drink id: %s not found...skipping" % (drink_id)
        elif line.find('Drink order presented') >= 0:
            try:
                time_stamp, time_struct = getTimestamp(line)
            except:
                #print "Caught exception..."
                continue
            drink_id = line[ line.rfind(':')+2 : line.rfind('.') ]
            if drink_id in drink_data:
                drink_data[drink_id]['presented_ts'] = time_stamp
                drink_data[drink_id]['state'] = STATE_PRESENTED
                # time_base[1] = timestamp
                # delta = drink_data[drink_id][3] - drink_data[drink_id][2]
                # drink_data[drink_id].append(delta)
            else:
                print "Drink id: %s not found...skipping" % (drink_id)

    print "Total drinks processed: %d" % (len(drink_data))
    print "Restarts              : %d" % (restarts)
    format = "%m/%d/%Y %H:00"
    # for (key, count_lst) in drink_count.iteritems():
    #     print "Drinks per hour: %s = %d" % (time.strftime(format, count_lst[1]), count_lst[0])
    # for key in sorted(drink_count.iterkeys()):
    #     count_lst = drink_count[key]
    #     print "Drinks per hour: %s = %d" % (time.strftime(format, count_lst[1]), count_lst[0])

    current_period = ""
    current_day = 0
    total_drinks = 0
    total_fails  = 0
    total_redos  = 0
    drinks_per_hour = 0
    fails_per_hour = 0
    redos_per_hour  = 0
    drink_type = defaultdict(int)
    daily_drink_type = defaultdict(int)
    overall_drink_type = defaultdict(int)
    overall_drinks_per_hour = defaultdict(int)    

    print "*******************************************\n** Drink Metrics **\n*******************************************"
    for drink_id in sorted(drink_data.iterkeys()):
        drink = drink_data[drink_id]
        drink_started_period = "%d.%d" % (drink['start_time_struct'].tm_yday, drink['start_time_struct'].tm_hour)

        if current_period != drink_started_period:
            if drinks_per_hour > 0:
                print " ------------------------------------------\n Summary for period: %s" % ( time.strftime(format, previous_time_struct) )
                #print previous_time_struct
                print "  Drinks made   : %d" % (drinks_per_hour)
                print "  Failed drinks : %d" % (fails_per_hour)
                print "  Redos         : %d" % (redos_per_hour)
                print "  Breakdown of drink type:"
                for (key, value) in drink_type.iteritems():
                    print "    %s = %d" % (key, drink_type[key])
                print "*******************************************\nNew period: %s...raw data:" % ( time.strftime(format, drink['start_time_struct']) )
            current_period = drink_started_period
            drinks_per_hour = 0
            fails_per_hour = 0
            redos_per_hour  = 0
            drink_type = defaultdict(int)
        current_day = drink['start_time_struct'].tm_yday
        try:
            if drink['state'] == STATE_PRESENTED:
                print "  %s (%s): time to make (sec): %s %s" % (drink['drink_type'], drink_id, (drink['complete_ts'] - drink['start_ts']), ("Redo!!" if drink['restart'] else ""))
                drinks_per_hour += 1
                total_drinks += 1
                if drink['restart']:
                    redos_per_hour += 1
                    total_redos += 1
                drink_type[drink['drink_type']] += 1
                overall_drink_type[drink['drink_type']] += 1
                overall_drinks_per_hour[drink['start_time_struct'].tm_hour] += 1
            else:
                print "  %s: Never made it to presenter" % (drink['drink_type'])
                fails_per_hour += 1
                total_fails += 1
            previous_time_struct = drink['start_time_struct']
        except:
            print "Caught exception"
            continue
    print " ------------------------------------------\n Summary for period: %s" % ( time.strftime(format, drink['start_time_struct']) )
    print "  Drinks made   : %d" % (drinks_per_hour)
    print "  Failed drinks : %d" % (fails_per_hour)
    print "  Redos         : %d" % (redos_per_hour)
    print "  Breakdown of drink type:"
    for (key, value) in drink_type.iteritems():
        print "    %s = %d" % (key, drink_type[key])
    print "*******************************************\n\n Overall Summary\n --------------------------------------------- "
    print "  Earliest drink processed: %s" % (time.strftime(format, timestamp_min_max[0]) )
    print "  Latest drink processed  : %s" % (time.strftime(format, timestamp_min_max[1]) )
    print "  Drinks made             : %d" % (total_drinks)
    print "  Failed drinks           : %d" % (total_fails)
    print "  Redos                   : %d" % (total_redos)
    print "  Breakdown of drink type:"
    for (key, value) in overall_drink_type.iteritems():
        print "    %s = %d" % (key, overall_drink_type[key])
    print "  Breakdown by hour:"
    for (key, value) in overall_drinks_per_hour.iteritems():
        print "    %02d:00 = %d" % (key, overall_drinks_per_hour[key])



