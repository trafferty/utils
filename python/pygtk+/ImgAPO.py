#!/usr/bin/env python

import signal
import sys
import json
import argparse
import time
from threading import Timer

from imgAPO_GUI import ImgAPO_GUI
from guiEventProcessor import GUIEventProcessor

class ImgAPOEventProcessor(GUIEventProcessor):
    """ garage Event Processor object"""

    def __init__(self, log_file):
        super(ImgAPOEventProcessor, self).__init__(log_file, "")
        #GUIEventProcessor.__init__(self, log_file, "")

    def eventCB(self, cb_dict):
        if cb_dict['event'] == 'ack':
            self.doLog('Callback connected...')

        elif cb_dict['event'] == 'start':
            self.start()

        elif cb_dict['event'] == 'stop':
            self.stop()

        elif cb_dict['event'] == 'quit':
            self.doLog('Exiting because of quit command')

        else:
            self.doLog('Error! Unsupported event: ', cb_dict['event'])

    def start(self):
        self.doLog('Started...')

    def stop(self):
        self.doLog('Stopped...')


if __name__ == '__main__':

    def sigint_handler(signal, frame):
        print "\nCaught Ctrl-c..."
        alive = False
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser(description='Event processor for GUI')
    parser.add_argument('-l', '--log_file', type=str, default='', help='log file path for processor (optional)', required=False)
    args = parser.parse_args()

    gui = ImgAPO_GUI()
    eventProcessor = ImgAPOEventProcessor(args.log_file)

    gui.addCallback(eventProcessor.eventCB)

    gui.run()
