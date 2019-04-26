import sys
import argparse
from struct import unpack, pack
import numpy as np
#from pylab import *
import matplotlib.pyplot as plt

def fft(inFile, bins):
    v49Start = '39345356'
    #v49Start = ['94', 'SV']
    #v49Start = '94SV'
    FFTEnd = '34127856'
    payloadOffset = 24
    payloadSize = 120
    cnt = 0
    FFTcnt = 0
    insideFFT = False
    #newFFT_np = np.empty((args.bins), dtype=np.uint16)
    FFT_list = []
    FFT = []
    try:
    	x = range(0, bins)
    	pltData, = plt.plot([], [])
    	#plt.ion()
        data = inFile.read(4)
        while data != "":
            #print data.encode('hex')
            if data.encode('hex') == v49Start:  #found start of header (VS49)
                cnt += 1
                #print "Found new record.  Count = %d" % (cnt)
                discard = inFile.read(payloadOffset)  # discard header data, go straight to payload
                for idx in range(0, payloadSize):
                    data = inFile.read(4)
                    if data.encode('hex') != FFTEnd:
                        # I have deal with endianess here, and break the 32bit word into 2 16bit words.
                        data_unpacked = unpack('2h', pack('>I', int(data.encode('hex'), 16)))
                        # newFFT_np[idx]   = data_unpacked[0]
                        # newFFT_np[idx+1] = data_unpacked[1]
                        FFT.append(data_unpacked[0])
                        FFT.append(data_unpacked[1])
                        #print "%d: %d/%d " % (idx, data_unpacked[0], data_unpacked[1]);
                        FFTcnt += 2
                    else:
                        print "Extracted %d 16-bit words into FFT" % (len(FFT))
                        if len(FFT) == bins:
                            print "Plotting FFT"
                            FFT_list.append(FFT)
                            FFT_np = np.array(FFT)
                            FFT_np = FFT_np*FFT_np
                            FFT_np = np.fft.fftshift(FFT_np)
                            FFT_np = 20*np.log10(FFT_np)
                            FFT_np = FFT_np-190+11.17 
                            #plt.cla()
                            x = range(0, bins)
                            ## ax = plt.subplot(111)
                            #plt.plot(x, FFT_np)
                            #plt.show()
                            pltData.set_xdata(x)
                            pltData.set_ydata(FFT_np)
                            plt.draw()

                        # newFFT_np = np.empty((args.bins), dtype=np.uint16)
                        FFT = []
                        insideFFT = False
                        FFTcnt = 0
                        break
                data = inFile.read(4)
            else:
                data = inFile.read(4)

    finally:
        inFile.close()

    print "Extracted %d FFTs" % (len(FFT_list))

    # ion()

    # x = arange(0,2*pi,0.01)            # x-array
    # line, = plot(x,sin(x))
    # for i in arange(1,200):
    #     line.set_ydata(sin(x+i/10.0))  # update the data
    #     draw()                         # redraw the canvas

    # FFT_np = np.array(FFT_list[0])
    # FFT_np = FFT_np*FFT_np
    # FFT_np = np.fft.fftshift(FFT_np)
    # FFT_np = 20*np.log10(FFT_np)
    # FFT_np = FFT_np-190+11.17
    return FFT_list

def fft_plot(fft, result_set, bins=512):
    plt.cla()
    x = range(0,bins)
    plt.plot(x, fft[result_set])
    plt.show()
    #ion()
    # for FFT in FFT_list:
    #     FFT_np = np.array(FFT)
    #     # FFT_np = FFT_np*FFT_np
    #     # FFT_np = np.fft.fftshift(FFT_np)
    #     # FFT_np = 20*np.log10(FFT_np)
    #     # FFT_np = FFT_np-190+11.17
    #     #hl.set_xdata(np.append(hl.get_xdata(), x))
    #     hl.set_ydata(FFT_np)
    #     draw()

    
    # fig = plt.figure()
    # ax = fig.add_subplot(111)

    # ion()

    # FFT_np = np.array(FFT_list[0])
    # FFT_np = FFT_np*FFT_np
    # FFT_np = np.fft.fftshift(FFT_np)
    # FFT_np = 20*np.log10(FFT_np)
    # FFT_np = FFT_np-190+11.17 
    # line, = ax.plot(x,FFT_np)

    # for FFT in FFT_list[len(FFT_list)-1]:
    #     FFT_np = np.array(FFT_list[len(FFT_list)-1])
    #     FFT_np = FFT_np*FFT_np
    #     FFT_np = np.fft.fftshift(FFT_np)
    #     FFT_np = 20*np.log10(FFT_np)
    #     FFT_np = FFT_np-190+11.17 
    #     line.set_ydata(FFT_np)
    #     fig.canvas.draw()

    # # x = range(0,args.bins)
    # # ax = plt.subplot(111)
    # # ax.plot(x,FFT_np)
    # # plt.show()
    
if __name__ == "__main__":
    '''
    FFTV49.py v49DataFile
    '''
    parser = argparse.ArgumentParser(description='Parse V49 records from either a file or stdin, extract FFT data, and plot')
    parser.add_argument('-i', '--inFile', dest='inFile', type=str,
                        help='input file...if not specified then use stdin')
    parser.add_argument('-b', '--bins', dest='bins', type=int, default=512,
                        help='num bins')
    args = parser.parse_args()

    if args.inFile:
        inFile = open(args.inFile, 'rb')
    else:
        inFile = sys.stdin
    
    print "Using %d as num bins" % args.bins

    y = fft(inFile, args.bins)
    fft_plot(y, 0)
    raw_input('Press a key for next result set')
    fft_plot(y, 1)
    raw_input('Press a key to exit')
