#!/usr/bin/env python

import sys
import argparse
from struct import unpack, pack
from colors import *

PrintColors = (BRIGHT_YELLOW, BRIGHT_CYAN)

def printHeader():
    #        123456      12345   123456  12345  12345 12345     1234567890  12345  12345   12345   123456
    print "%s----------------------------------------------------------------------------------------------%s" % (WHITE, RESET)
    print "%s   Rec     FFT Frame  Pack  Pack  Strm   Num   Timestamp  FFT                Freq  %s" % (WHITE, RESET)
    print "%s   Num     Set   Cnt   Cnt  Type    ID   Bin   sec (UTC)  Data                MHz  %s" % (WHITE, RESET)
    print "%s----------------------------------------------------------------------------------------------%s" % (WHITE, RESET)

def AnalyzeFFT(inFile):
    v49Start = '39345356'
    v49End   = '444e4556'
    FFTEnd   = '34127856'
    wordSize = 4
    frameDataOffset  = 2 * wordSize
    packetDataOffset = 3 * wordSizeq
    StreamBinOffset  = 4 * wordSize
    timeOffset       = 5 * wordSize
    freqOffset       = 6 * wordSize
    payloadOffset    = 7 * wordSize
    payloadSize      = 120 * wordSize
    prevPacket = prevFrame = prevTime = -1
    recCnt = FFTSet = 0
    insideFFT = False
    newColor = 0
    printHeader()
    try:
        data = inFile.read(wordSize)
        while data != "":
            #print data.encode('hex')
            if data.encode('hex') == v49Start:  #found start of header (VS49)
                FFTDataCnt = FFTEndCnt = 0
                if recCnt > 1: 
                    prevFrame = newData['frameCnt']
                    prevPacket = newData['packetCnt']
                    prevTime = newData['time_Sec']
                v49Loc = wordSize
                newData = {}
                newData['FFTDataCnt'] = newData['FFTEndCnt'] = newData['EndsBeforeData'] = newData['DataAfterEndS'] = 0
                recCnt += 1
            elif data.encode('hex') == v49End:  #found end of header (VEND)
                if (recCnt > 1) and ((newData['frameCnt']-prevData['frameCnt']) > 1):
                    
                    #formattedData = '{frameCnt:% 5d}  {packetCnt:% 4d}  {packetType:% 4d}  % 4d % 5d  % 10d  %3d:%-03d (%3d)  %07.3f'.format(**newData)
                    
                    print("%s% 6d % 6d  % 5d  % 4d  % 4d  % 4d % 5d  % 10d  %3d:%-03d (%3d,%3d)  %07.3f%s" % 
                        (BRIGHT_RED, recCnt, FFTSet, newData['frameCnt'], newData['packetCnt'], newData['packetType'],
                        newData['streamID'], newData['binSize'], newData['time_Sec'], newData['FFTDataCnt'],
                        newData['FFTEndCnt'], newData['EndsBeforeData'], newData['DataAfterEndS'], newData['currFreq_MHz'], RESET))
                else:
                    print("%s% 6d % 6d  % 5d  % 4d  % 4d  % 4d % 5d  % 10d  %3d:%-03d (%3d,%3d)  %07.3f%s" % 
                        (PrintColors[newColor], recCnt, FFTSet, newData['frameCnt'], newData['packetCnt'], newData['packetType'], 
                        newData['streamID'], newData['binSize'], newData['time_Sec'], newData['FFTDataCnt'],
                        newData['FFTEndCnt'], newData['EndsBeforeData'], newData['DataAfterEndS'], newData['currFreq_MHz'], RESET))
                if newData['packetCnt'] == 15:
                    printHeader()
                    packetCnt = -1
                if newData['frameCnt'] == 4095:
                    newData['frameCnt'] = -1
                if not insideFFT:
                    newColor ^= 1
                    FFTSet += 1
                prevData = newData
            else:
                v49Loc += wordSize
                if v49Loc < payloadOffset:
                    fixed_data = unpack('I', pack('>I', int(data.encode('hex'), 16)))[0]   # fix endianness
                    if v49Loc == frameDataOffset:
                        newData['frameCnt']  = fixed_data >> 20
                        newData['frameSize'] = fixed_data & 0xfffff
                    elif v49Loc == packetDataOffset:
                        newData['packetCnt'] = (fixed_data >> 16) & 0x0F
                        newData['packetType'] = fixed_data >> 28
                    elif v49Loc == StreamBinOffset:
                        newData['streamID'] = fixed_data & 0xFF
                        newData['IQG_field'] = (fixed_data >> 8) & 0x0F
                        newData['binSize'] = pow(2, newData['IQG_field'])
                        #binSize = IQG_field
                    elif v49Loc == timeOffset:
                        newData['time_Sec'] = fixed_data
                    elif v49Loc == freqOffset:
                        newData['currFreq_MHz'] = fixed_data / 1.0e6
                else:
                    if 1:
                        for idx in range(0, (payloadSize / wordSize)):
                            if data.encode('hex') != FFTEnd:
                                newData['FFTDataCnt'] += 2
                                insideFFT = True
                            else:
                                newData['FFTEndCnt'] += 2
                                insideFFT = False
                            data = inFile.read(wordSize)
                    else:
                        # Now just read all the payload and analyze
                        #cnt = 0
                        #print "v49Loc = %d, first data = %s" % (v49Loc, data.encode('hex'))
                        gotFFTEnd = False
                        recData = recEnds = 0
                        while  v49Loc < (payloadOffset + payloadSize):
                            if data.encode('hex') != FFTEnd:
                                recData += 1
                                if recEnds > 0: newData['DataAfterEndS'] += 1
                            else:
                                recEnds += 1
                                gotFFTEnd = True
                                if recData == 0: newData['EndsBeforeData'] += 1
                            data = inFile.read(wordSize) 
                            v49Loc += wordSize
                        newData['FFTDataCnt'] += (2 * recData)
                        newData['FFTEndCnt']  += (2 * recEnds)
                        insideFFT = False if gotFFTEnd else True
                        #print "payload cnt = %d, last data = %s" % (cnt, data.encode('hex'))
            data = inFile.read(4)


    finally:
        inFile.close()
    
if __name__ == "__main__":
    '''
    Analyze_FFTV49.py v49DataFile
    '''
    parser = argparse.ArgumentParser(description='Parse V49 records from either a file or stdin, extract FFT data, and analyze')
    parser.add_argument('-i', '--inFile', dest='inFile', type=str,
                        help='input file...if not specified then use stdin')
    args = parser.parse_args()

    if args.inFile:
        inFile = open(args.inFile, 'rb')
    else:
        inFile = sys.stdin
    
    AnalyzeFFT(inFile)
    inFile.close()
