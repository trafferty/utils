import os 
import sys
import argparse
import math
import time
from struct import unpack, pack
import numpy as np
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import matplotlib
# matplotlib needs a window framework, lets use QT4
matplotlib.use('Qt4Agg')

from colors import *
import lineplot

PrintColors = (BRIGHT_YELLOW, BRIGHT_CYAN)

# before use, set an env var pointing to the top of the proto dir, ie, .../TacticalSensorStack/libsensorservice/proto
TGI_PROTO_DIR = os.getenv("TGI_PROTO_DIR")

# to allow importing of services.sensor.ss_*
sys.path.append(os.path.abspath(TGI_PROTO_DIR))

# now import the GPB definitions
import services.sensor.ss_pb2 as pb
import services.sensor.ss_dataproduct_pb2 as dp

# for plot, this is the x-axis tick size
xtick_width_MHz = 1.0

def Process_PSD_Stream(inFile, plt):
    """Processes a stream of PSD data in the form of GPBs according to ss_dataproduct

    Args:
        inFile: the file handle for the input stream
        plt   : handle to the lineplot opbject to use (see lineplot.py)
    Returns:
        none...returns when stream is empty
    Raises:
        none. 

    """
    prev_group_id = -1
    # create a dict for metrics, and initialize
    metrics = {}
    metrics['bytes_read']      = 0
    metrics['data_rate_Mbps']  = 0.0
    metrics['elapsed_time_s']  = 0.0
    metrics['start_time_ts']   = time.time()
    metrics['sweep_count']     = 0.0
    metrics['sweeps_per_sec']  = 0.0

    try:
        in_buf = inFile.read(4)
        while in_buf != "":
            size = int(in_buf.encode('hex'), 16)
            #size = unpack('I', pack('<I', int(data.encode('hex'), 16)))[0]
            # read in the data_product
            rawGPB = inFile.read(size)
            metrics['bytes_read'] += size
            data_response = pb.DataResponse()
            data_response.ParseFromString(rawGPB)
            for data_prod in data_response.data_products:
                if data_prod.HasExtension(dp.power_spectrum_data):
                    power_spec_data = data_prod.Extensions[dp.power_spectrum_data]  
                    # read the data portion into a numpy array                  
                    data_np = np.frombuffer(power_spec_data.spectrum_data.data, dtype=np.int16)
                    # grab the header data
                    start_freq_mhz  = (power_spec_data.header.start_freq_hz / 1.0e6)
                    end_freq_mhz    = (power_spec_data.header.end_freq_hz   / 1.0e6)
                    inc_mhz         = (end_freq_mhz - start_freq_mhz) / len(data_np)
                    # print some stats
                    print_PSD_Stats(data_np, power_spec_data.header, power_spec_data.spectrum_data.format, 
                                    (prev_group_id < power_spec_data.header.group_id), metrics['data_rate_Mbps'], metrics['sweeps_per_sec'])
                    # now either append to the plot data, or if we have a full spectrum, plot it
                    if prev_group_id < power_spec_data.header.group_id and plt != None:
                        if 'plot_data_np' in locals():
                            plt.ylim   = (min(plot_data_np) - 20, max(plot_data_np) + 20)
                            plt.xlim   = (min(x), max(x))
                            plt.set_data((x, plot_data_np))
                            plt.xticks = xticks
                            plt.xlabel = "MHz  - [Bins: %d, Incr (kHz): %4.1f, GroupId: %d]" % ( len(data_np), (inc_mhz * 1000), power_spec_data.header.group_id )
                            plt.title = "Power Spectrum Density - [Sweeps per sec: %f, Data rate (Mbps): %f]" % (metrics['sweeps_per_sec'], metrics['data_rate_Mbps'])
                        #print "Starting new plot data..."
                        plot_data_np = data_np
                        x            = np.linspace(start_freq_mhz, start_freq_mhz + (len(data_np) * inc_mhz), len(data_np), False) 
                        xticks       = np.arange(start_freq_mhz, end_freq_mhz, xtick_width_MHz).tolist()
                        metrics['sweep_count'] += 1.0
                    else:
                        plot_data_np = np.append(plot_data_np, data_np)
                        x            = np.append(x, np.linspace(start_freq_mhz, start_freq_mhz + (len(data_np) * inc_mhz), len(data_np), False) )
                        for xtick in np.arange(start_freq_mhz, end_freq_mhz, xtick_width_MHz).tolist(): xticks.append(xtick)
                    prev_group_id = power_spec_data.header.group_id
            in_buf = inFile.read(4)
            # do some metrics on data to determine data rate
            metrics['elapsed_time_s'] = time.time() - metrics['start_time_ts']
            if metrics['elapsed_time_s'] >= 2.0:
                metrics['data_rate_Mbps'] = ((metrics['bytes_read'] * 8 ) / (metrics['elapsed_time_s'] * 1024 * 1024 ))
                metrics['sweeps_per_sec'] = ( metrics['sweep_count'] / metrics['elapsed_time_s'] )
                metrics['bytes_read']     = 0
                metrics['start_time_ts']  = time.time()
                metrics['elapsed_time_s'] = 0.0
                metrics['sweep_count']    = 0
    finally:
        inFile.close()

def print_PSD_Stats(data_np, header, format, print_header, data_rate_Mbps, sweeps_per_sec):
    inc_mhz         = ((header.end_freq_hz   / 1.0e6) - (header.start_freq_hz / 1.0e6)) / len(data_np)
    if print_header and not header.group_id % 5:
        #        123456    12345   123456   12345    12345   12345 12345  1234567  1234567  1234567  1234  1234  1234  1234567    12345
        print "%s------------------------------------------------------------------------------------------------------------------------%s" % (WHITE, RESET)
        print "%s Group     Data    Bits/          Scaling                  Start      End   Incr                    DataRate  Sweeps/ %s" % (WHITE, RESET)
        print "%s    ID     Len     Value  Signed   Factor  Offset  Comp     Freq     Freq  (kHz)   Max   Min  Mean   (Mbps)     sec   %s" % (WHITE, RESET)
        print "%s------------------------------------------------------------------------------------------------------------------------%s" % (WHITE, RESET)
    print("%s% 6d   % 6d    % 5d  % 6d    % 5d  % 5d  % 5d  %07.3f  %07.3f  %05.1f  % 4d  % 4d  % 4d  %07.3f    %04.1f%s" % 
        (PrintColors[header.group_id%2], header.group_id, len(data_np),
        format.bits_per_value, format.signed, format.scaling_factor, format.offset, 
        format.compression, (header.start_freq_hz / 1.0e6), (header.end_freq_hz   / 1.0e6), (inc_mhz * 1000), 
        data_np.max(), data_np.min(), data_np.mean(), data_rate_Mbps, sweeps_per_sec, RESET))

class GPBProcess(QThread):
	def run(self):
		Process_PSD_Stream(self.inFile, self.plt)
		
if __name__ == "__main__":
    '''
    process_PSD.py GPBDataFile
    '''
    parser = argparse.ArgumentParser(description='Processes a stream of GPBs, extracting PSD data, from either a file or stdin, analyze and (optionally) plot')
    parser.add_argument('-i', dest='in_file', type=str, help='input file...if not specified then use stdin')
    parser.add_argument('-p', dest='do_plot', type=bool, default=True, help='plot data.  default is True')
    args = parser.parse_args()
    
    # matplotlib needs a window framework...we use QT4, so we need to create a QApplication
    qapp = QApplication([])
    
    if args.do_plot:
        plt = lineplot.LinePlotWidget(title="Power Spectrum")
        plt.show()
    else:
        print "No plotting!"
        plt = None

    plt.ylabel = "dBm"
    plt.xlabel = "MHz"

    if args.in_file:
        inFile = open(args.in_file, 'rb')
    else:
        inFile = sys.stdin
    
    #QTimer.singleShot(1000, lambda: Process_PSD_Stream(inFile, plt))
    gpb_process = GPBProcess()
    gpb_process.inFile = inFile
    gpb_process.plt = plt
    QTimer.singleShot(100, gpb_process.start)

    qapp.exec_()
