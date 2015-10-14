#!/usr/bin/env python

import signal
import socket
import sys
import json
import argparse
import time
import threading

from imgAPO_GUI import ImgAPO_GUI
from guiEventProcessor import GUIEventProcessor

(STOPPED, RUNNING) = range(2)

class ImgAPOEventProcessor(GUIEventProcessor):
    """ garage Event Processor object"""

    def __init__(self, ip, port, log_file):
        super(ImgAPOEventProcessor, self).__init__(log_file, "")

        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect((ip, port))

        self.alive = True
        # start socket reading
        self.socketRead_thread = threading.Thread(target=self.read_socket)
        self.socketRead_thread.setDaemon(1)
        self.socketRead_thread.start()
        self.state = RUNNING

        self.looping = False

    def eventCB(self, cb_dict):
        if cb_dict['event'] == 'ack':
            self.doLog('Callback connected...')

        elif cb_dict['event'] == 'start':
            self.looping = False
            self.start()

        elif cb_dict['event'] == 'stop':
            self.looping = False
            self.stop()

        elif cb_dict['event'] == 'loop':
            if self.looping == False:
                self.looping = True
                self.loop_thread = threading.Thread(target=self.loop_cmds)
                self.loop_thread.setDaemon(1)
                self.loop_thread.start()

        elif cb_dict['event'] == 'quit':
            self.doLog('Exiting because of quit command')
            self.looping = False
            self.alive = False
            self.state = STOPPED
            self.socketRead_thread.join()
            self.loop_thread.join()

        else:
            self.doLog('Error! Unsupported event: ', cb_dict['event'])

    def read_socket(self):
        while self.alive:
            line = self.clientsocket.recv(1024)
            print line,
            time.sleep(.01)

    def loop_cmds(self):
        cmd_lst = ['{"method":"start"}\n', '{"method":"stop"}\n']
        cmd_num = 0
        iter_cnt = 0
        while self.looping:
            iter_cnt += 1
            self.doLog("(looping) Starting loop %d" % (iter_cnt))
            self.clientsocket.send(cmd_lst[cmd_num])
            time.sleep(8)
            cmd_num = cmd_num ^ 1

    def start(self):
        self.doLog('Starting...')
        self.clientsocket.send('{"method":"start"}\n')

    def stop(self):
        self.doLog('Stopping...')
        self.clientsocket.send('{"method":"stop"}\n')

if __name__ == '__main__':

    def sigint_handler(signal, frame):
        print "\nCaught Ctrl-c..."
        alive = False
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser(description='Event processor for GUI')
    parser.add_argument('-l', '--log_file', type=str, default='', help='log file path for processor (optional)', required=False)
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='ip address (def: 127.0.0.1)', required=False)
    parser.add_argument('-p', '--port', type=int, default=12070, help='Port number to connect to (def: 12070)', required=False)
    args = parser.parse_args()

    gui = ImgAPO_GUI()
    eventProcessor = ImgAPOEventProcessor(args.ip, args.port, args.log_file)

    gui.addCallback(eventProcessor.eventCB)

    gui.run()
