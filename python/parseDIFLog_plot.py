#!/usr/bin/env python

import sys
import time
import re
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

def parseDIFLog(DIFLog):
    '''
    import re
    p = re.compile(ur'\ (?P<start1_ts>[0-9:]*),\ (?P<dif_mem>[0-9.]*),\ (?P<dif_cpu>[0-9.]*),\ (?P<sys_mem>[0-9.]*)\n', re.DOTALL)
    test_str = u"militho     5889  0.0    ?   24100    6844 /dev/pts/13   16:29   00:00  bash\nroot        5921  0.0    ?   89564    4572 /dev/pts/11   16:29   00:00  sudo\nmilitho     5922  0.0    ?    7208    1860 /dev/pts/11   16:29   00:04  tee\nroot        5923  0.0  0.9  180140  140808 /dev/pts/11   16:29   00:01  gdb\nroot        5925 91.3 20.1 4870632 3284572 /dev/pts/11   16:29   11:16  dif\nmilitho     5960  0.3  0.3  913356   41640 /dev/pts/12   16:29   00:58  python3\nmilitho     5992  0.1  0.1   47908   12636 /dev/pts/13   16:31   00:11  python3\nmilitho     5993  0.0    ?    7208    1752 /dev/pts/13   16:31   00:00  tee\nmilitho     6001  0.0    ?   24080    6828 /dev/pts/6    16:31   00:00  bash\nroot        6205  0.2    ?       ?       ? ?             17:28   00:08  kworker/u66:1\nroot        6229  0.0    ?       ?       ? ?             17:52   00:00  kworker/3:0\nroot        6230  0.0    ?       ?       ? ?             17:53   00:05  kworker/0:0\nroot        6240  0.0    ?       ?       ? ?             18:03   00:00  kworker/1:0\nroot        6242  0.0    ?       ?       ? ?             18:04   00:02  kworker/5:0\nroot        6249  0.0    ?       ?       ? ?             18:10   00:01  kworker/6:2\nroot        6255  0.0    ?       ?       ? ?             18:15   00:01  kworker/7:0\nroot        6261  0.0    ?       ?       ? ?             18:18   00:00  kworker/u65:0\nroot        6263  0.0    ?       ?       ? ?             18:24   00:00  kworker/2:0\nroot        6264  0.0    ?       ?       ? ?             18:25   00:07  kworker/4:2\nroot        6271  0.0    ?       ?       ? ?             18:33   00:02  kworker/0:2\nroot        6274  0.3    ?       ?       ? ?             18:36   00:07  kworker/4:3\nroot        6276  0.0    ?       ?       ? ?             18:39   00:00  kworker/u65:2\nroot        6277  0.0    ?       ?       ? ?             18:41   00:00  kworker/3:1\nroot        6278  0.0    ?       ?       ? ?             18:42   00:00  kworker/u66:2\nroot        6283  0.0    ?       ?       ? ?             18:50   00:00  kworker/u66:0\nNone\nWed 18:53:01, 20.083838, 91.80, 25.30\nWed 18:53:11, 20.216892, 98.90, 25.80\nWed 18:53:21, 20.678593, 90.40, 25.80\nWed 18:53:31, 20.810742, 93.00, 26.40\nWed 18:53:41, 21.272688, 88.00, 26.70\nWed 18:53:51, 21.602656, 95.20, 27.00\nWed 18:54:01, 21.867760, 85.90, 27.10\nWed 18:54:11, 21.999933, 93.80, 27.60\nWed 18:54:21, 22.462319, 86.50, 27.90\nWed 18:54:31, 22.791798, 92.90, 28.00\nUSER         PID %CPU %MEM     VSZ     RSS TTY           START    TIME  COMMAND\nroot           1  0.0    ?   33912    4256 ?             08:57   00:56  init\nroot           2  0.0    ?       ?       ? ?             08:57   00:00  kthreadd\nroot           3  0.0    ?       ?       ? ?             08:57   00:01  ksoftirqd/0\nroot           5  0.0    ?       ?       ? ?             08:57   00:00  kworker/0:0H\nroot           6  0.0    ?       ?       ? ?             08:57   00:00  kworker/u64:0\nroot           8  0.1    ?       ?       ? ?             08:57   01:43  rcu_sched\nroot           9  0.0    ?       ?       ? ?             08:57   00:00  rcu_bh\n"
     
    re.findall(p, test_str)    '''
        
    DIF_ps_pattern=ur'\ (?P<log_ts>[0-9:]*),\ (?P<dif_mem>[0-9.]*),\ (?P<dif_cpu>[0-9.]*),\ (?P<sys_mem>[0-9.]*)\n'

    f = open(DIFLog, 'r')
    buf = f.read()
    f.close()
    print "File (%s) opened and read into buffer, length of buf: %d" % (DIFLog, len(buf))

    DIF_ps_sets = [x.groupdict() for x in re.finditer(DIF_ps_pattern, buf)]
    print "Parsing log for DIF_ps...found %d records." % (len(DIF_ps_sets))
    if len(DIF_ps_sets) > 0: print " >> Timestamp range: %s - %s" % (DIF_ps_sets[0]['log_ts'], DIF_ps_sets[-1]['log_ts'])

    timestamp_format = "%H:%M:%S"

    start_ts = dt.datetime.strptime(DIF_ps_sets[0]['log_ts'], timestamp_format)

    DIF_mem = []
    DIF_cpu = []
    sys_mem = []
    elapsed_times = []
    for idx, DIF_ps_set in enumerate(DIF_ps_sets):
        '''
        Wed 18:53:01, 20.083838, 91.80, 25.30
        Wed 18:53:11, 20.216892, 98.90, 25.80
        Wed 18:53:21, 20.678593, 90.40, 25.80
        Wed 18:53:31, 20.810742, 93.00, 26.40
        Wed 18:53:41, 21.272688, 88.00, 26.70
        Wed 18:53:51, 21.602656, 95.20, 27.00
        Wed 18:54:01, 21.867760, 85.90, 27.10
        Wed 18:54:11, 21.999933, 93.80, 27.60
        Wed 18:54:21, 22.462319, 86.50, 27.90
        Wed 18:54:31, 22.791798, 92.90, 28.00
        '''
        #if idx % 1 == 0:
        log_ts = dt.datetime.strptime(DIF_ps_set['log_ts'], timestamp_format)
        delta = log_ts - start_ts
        elapsed_times.append(delta.seconds/10)
        DIF_mem.append(DIF_ps_set['dif_mem'])
        DIF_cpu.append(DIF_ps_set['dif_cpu'])
        sys_mem.append(DIF_ps_set['sys_mem'])
    
    DIF_mem_np = np.array(DIF_mem)
    DIF_cpu_np = np.array(DIF_cpu)
    sys_mem_np = np.array(sys_mem)
    elapsed_times_np = np.array(elapsed_times)
    
    print("%d -> %d" % (elapsed_times[0], elapsed_times[-1]))
    xticks = np.arange(min(elapsed_times), max(elapsed_times)+1, len(elapsed_times)/12)
    print(xticks)
    print(len(DIF_mem))

    if len(DIF_mem) > 0:
        fig = plt.figure(figsize=(10*2,5))
        ax = fig.add_subplot(111)
        ax.set_title('DIF Percent Memory')
        ax.set_ylabel('% mem')
        ax.set_xlabel('Elapsed time (each point is 10s)')
        #ax.xaxis.set_ticks(ange(len(elapsed_times)), elapsed_times_np)
        ax.xaxis.set_ticks(xticks)
        ax.plot(DIF_mem_np, color='b', label='DIF % mem')
        ax.plot(sys_mem_np, color='g', label='System % mem')
        ax.legend()
        plt.show()

if __name__ == "__main__":
    '''
    parseDIFLog.py -i file_to_parse
    '''
    parser = argparse.ArgumentParser(description='open process log file, parse it according to parse function')
    parser.add_argument('-i', '--in_file', dest='in_file', type=str,
                        help='input file...if not specified then use stdin')

    args = parser.parse_args()

    if args.in_file:
        parseDIFLog(args.in_file)
    else:
        parser.print_help()
        sys.exit(1)
