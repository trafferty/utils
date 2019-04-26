#!/usr/bin/env python
import os 
import sys
import time
import argparse
import numpy as np
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
from PySide.QtGui import *
from PySide.QtCore import *

# lineplot.py needs to be in local folder:
import lineplot
from colors import *

PrintColors = (BRIGHT_YELLOW, BRIGHT_CYAN)

def PlotDataStream(inFile, plt, pts_to_plot, plot_sets, data_terminator, plot_title):
    print "%s Pts to plot:%s %d%s" % (BRIGHT_CYAN, BRIGHT_YELLOW, pts_to_plot, RESET)
    print "%s Plot sets  :%s %d%s" % (BRIGHT_CYAN, BRIGHT_YELLOW, plot_sets, RESET)
    print "%s Data term  :%s %s%s" % (BRIGHT_CYAN, BRIGHT_YELLOW, data_terminator, RESET)
    metrics = {}
    metrics['bytes_read']   = 0
    metrics['total_data_pts']   = 0
    metrics['min_data_pt']   = 0.0
    metrics['max_data_pt']   = 0.0
    metrics['recent_min_data_pt']   = 0.0
    metrics['recent_max_data_pt']   = 0.0
    metrics['stats_set']   = 0
    metrics['data_set']   = 0
    print_metric_count = 100
    start_time = time.time()

    buf_lst = []
    data_pts = []
    data_pts_total_np = np.array([])
    plot_data_np = np.zeros((plot_sets*pts_to_plot), dtype=np.float)
    data_offset = -1 * pts_to_plot
    xtick_start = 1
    xtick_width = (plot_sets*pts_to_plot)/10.0

    try:
        buf = inFile.read(1)
        while buf != "":
            metrics['bytes_read'] += 1

            if buf != data_terminator:
                # not yet a full data point, just append to list
                buf_lst.append(buf)
            else:
                # we have a full data point...convert and append to data_pts
                data_pts.append(float(''.join(buf_lst)))
                buf_lst = []

            if len(data_pts) >= (pts_to_plot) and plt != None:
                metrics['data_set'] += 1
                plot_data_np = np.roll(plot_data_np, data_offset)
                plot_data_np[data_offset:] = data_pts
                data_pts_total_np = np.append(data_pts_total_np, data_pts)

                data_pts = []

                if metrics['data_set'] >= 1:
                    x          = np.linspace(xtick_start, (xtick_start+len(plot_data_np)), len(plot_data_np), False)
                    plt.ylim   = (np.min(plot_data_np) - 20, np.max(plot_data_np) + 20)
                    plt.xlim   = (min(x), max(x))
                    plt.xlabel = "Data points - Max: %d, Min %d, Median: %1.1f" % (np.max(plot_data_np), np.min(plot_data_np), np.median(plot_data_np))
                    plt.title  = plot_title
                    #plt.xticks = np.arange(xtick_start, (xtick_start+len(plot_data_np)), xtick_width).tolist()
                    plt.xticks = np.arange(min(x), max(x)+1, xtick_width)
                    plt.set_data((x, plot_data_np))
                    xtick_start += pts_to_plot

                '''   metrics:  '''
                metrics['total_data_pts']     = len(data_pts_total_np)
                metrics['min_data_pt']        = data_pts_total_np.min()
                metrics['max_data_pt']        = data_pts_total_np.max()
                metrics['mean_data_pt']       = data_pts_total_np.mean()
                metrics['recent_min_data_pt'] = plot_data_np.min()
                metrics['recent_max_data_pt'] = plot_data_np.max()
                metrics['recent_mean_data_pt'] = plot_data_np.mean()
                if metrics['total_data_pts'] % print_metric_count == 0:
                    metrics['read_rate_Kps'] = (metrics['bytes_read'] / (time.time() - start_time)) / float(1024)
                    metrics['stats_set'] += 1
                    printStats(metrics)
            buf = inFile.read(1)
    finally:
        inFile.close()

def printStats(metrics): 
    if metrics['stats_set'] == 1 or not metrics['stats_set'] % 25:
        #         12345678   12345678   12345678   12345678   12345678   12345 12345  1234567  1234567  1234567
        print "%s--------------------------------------------------------------------------+----------------------------------%s" % (BRIGHT_WHITE, RESET)
        print "%s Data      KBytes   Read Rate      Total        Max        Min       Mean |    Rec Max    Rec Min   Rec Mean %s" % (BRIGHT_WHITE, RESET)
        print "%s  Set        Read       (Kps)        Pts      Value      Value      Value |      Value      Value      Value %s" % (BRIGHT_WHITE, RESET)
        print "%s--------------------------------------------------------------------------+----------------------------------%s" % (BRIGHT_WHITE, RESET)
    print("%s% 5d     % 7.1f         %03.1f   % 8d    %07.1f    %07.1f    %07.1f %s|%s    %07.1f    %07.1f    %07.1f  %s" % 
        (PrintColors[metrics['stats_set']%2], metrics['stats_set'], (metrics['bytes_read']/1000.0), metrics['read_rate_Kps'], metrics['total_data_pts'],
        metrics['max_data_pt'], metrics['min_data_pt'], metrics['mean_data_pt'], BRIGHT_WHITE, PrintColors[metrics['stats_set']%2],
        metrics['recent_max_data_pt'], metrics['recent_min_data_pt'], metrics['recent_mean_data_pt'], 
        RESET))

class ProcessLoadcellData(QThread):
	def run(self):
		PlotDataStream(self.inFile, self.plt, self.pts_to_plot, self.plot_sets, self.data_terminator, self.plot_title)
		
if __name__ == "__main__":
    '''
    loadcell_analyze.py -i loadcell_data_file
    '''
    parser = argparse.ArgumentParser(description='Parse comma-delimeted loadcell data, from either a file or stdin, analyze and plot')
    parser.add_argument('-i', dest='in_file', type=str, help='input file...if not specified then use stdin')
    parser.add_argument('-p', dest='do_plot', type=bool, default=True, help='Do plot data (default: True)')
    parser.add_argument('-d', dest='pts_to_plot', type=int, default=25, help='Data pts to plot at a time (default: 25)')
    parser.add_argument('-s', dest='plot_sets', type=int, default=4, help='Plot sets (default: 4)')
    args = parser.parse_args()
    
    q = QApplication([])

    if args.do_plot:
        plt = lineplot.LinePlotWidget()
        plt.show()
    else:
        print "No plotting!"
        plt = None

    if args.in_file:
        inFile = open(args.in_file, 'rb')
    else:
        inFile = sys.stdin
    
    pd = ProcessLoadcellData()
    pd.inFile = inFile
    pd.plt = plt
    pd.pts_to_plot = args.pts_to_plot
    pd.plot_sets = args.plot_sets
    pd.data_terminator = ','
    pd.plot_title = "Loadcell Readings"

    QTimer.singleShot(100, pd.start)

    q.exec_()
