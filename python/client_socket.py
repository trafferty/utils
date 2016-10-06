#!/usr/bin/env python3

import socket
import threading
import argparse
import time

class ClientSocket(object):
    """
    Simple client for a socket, with a callback.

    Use as, for example:

        >>> c = ClientSocket(('localhost', 1234))
        >>> c.start()
        >>> c.setCallback = name_of_func_to_call_when_new_socket_data
        >>> c.stream.write('foo\n')  # send data to server

    The function 'listener_callback' will get called with the response
    of the server as an argument.
    """

    def __init__(self, name, server_address, log_file):
        self.name = name
        self.server_address = server_address
        self.connected = False

        self.callback_func = None

        self.log_file = log_file

    def doLog(self, log_msg):
        msg = "%s [%s]: %s" % (time.strftime("[%Y_%d_%m (%a) - %H:%M:%S]", time.localtime()), self.name, log_msg)
        print (msg)
        if len(self.log_file) > 0: 
            f = open(self.log_file, 'a')
            f.write(msg + '\n')
            f.close()

    def setCallback(self, callback_func):
        self.callback_func = callback_func

    def write(self, msg):
        self.clientsocket.send(('%s\n' % msg).encode('utf-8'))

    def start(self):
        """
        Start the listening thread
        """
        self.alive = True
        self.thread = threading.Thread(target=self._listener)
        self.thread.start()
        
    def stop(self):
        """
        Stop the listening thread
        """
        self.alive = False
        self.thread.join()
        self.connected = False
        self.clientsocket.close()

    def connected(self):
        return self.connected

    def _listener(self):
        self.doLog('Starting listening thread')
        while self.alive:
            read_ok, lines = self.read_socket()
            if read_ok:
                for line in lines:
                    self.callback_func(line)
            else:
                time.sleep(0.1)
        self.doLog('Finishing listening thread')

    def read_socket(self):
        lines = []
        if not self.connected:
            try:
                #self.doLog("Connecting to server at %s:%d" % (self.server_address[0], self.server_address[1]))
                self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.clientsocket.connect(self.server_address)
                self.clientsocket.settimeout(2)
                self.connected = True
                self.doLog("Connected to server at %s:%d" % (self.server_address[0], self.server_address[1]))
                self.buf = ''
            except socket.timeout:
                print("Socket timeout!")
                return False, lines
            except socket.error as e:
                #print("Socket error! " + str(e) )
                return False, lines

        try:
            data = self.clientsocket.recv(1024)
        except socket.timeout as e:
            err = e.args[0]
            if err == 'timed out':
                #self.doLog('recv timed out, retry later')
                return False, lines
            else:
                self.connected = False
                self.clientsocket.close()
                return False, lines
        except socket.error as e:
            print("Socket error! " + str(e))
            self.connected = False
            self.clientsocket.close()
            return False, lines
        else:
            if len(data) == 0:
                self.doLog('Server shut down...')
                self.connected = False
                self.clientsocket.close()
                return False, lines
            else:
                self.buf += data.decode('utf-8')
                idx = self.buf.find('\n')
                while idx >= 0:
                    lines.append(self.buf[:idx])
                    self.buf = self.buf[idx+1:]
                    idx = self.buf.find('\n')
            return True, lines

def test_callback_func(msg):
    print("Rec'd: " + msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client Socket class - Tester')
    parser.add_argument("port", type=int, help='Port on localhost to use')
    args = parser.parse_args()

    if args.port:
        port = args.port
    else:
        port = 5555
    
    c = ClientSocket('test', ('127.0.0.1', port), '')
    c.setCallback(test_callback_func)
    c.start()
    time.sleep(0.5)  # sleep a bit to allow reply

    msg = 'test 1'
    print("Sending msg: %s" % msg)
    c.write(msg)  # send cmd to server    
    time.sleep(0.5)  # sleep a bit to allow reply

    msg = 'test 2'
    print("Sending msg: %s" % msg)
    c.write(msg)  # send cmd to server    
    time.sleep(0.5)  # sleep a bit to allow reply

    msg = 'test 3'
    print("Sending msg: %s" % msg)
    c.write(msg)  # send cmd to server    
    time.sleep(0.5)  # sleep a bit to allow reply

    c.stop()
