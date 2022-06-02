#!/usr/bin/env python3

import socket
import threading
import argparse
import time
import logging, logging.config

class ClientSocket(object):
    """
    Simple client for a socket, with a callback.

    Use as, for example:

        >>> c = ClientSocket(('localhost', 1234))
        >>> c.start()
        >>> c.setCallback = name_of_func_to_call_when_new_socket_data
        >>> c.stream.write('foo\n')  # send data to server

    The callback function will get called with the response
    of the server as an argument.
    """

    def __init__(self, name, server_address):
        self.name = name
        self.server_address = server_address
        self.connected = False

        self.callback_func = None

        # assumes logging has been previous configured...
        self.logger = logging.getLogger(self.name)

    def setCallback(self, callback_func):
        self.callback_func = callback_func

    def write(self, msg):
        self.clientsocket.send(('%s\n' % msg).encode('utf-8'))

    def start(self):
        """
        Start the comm thread
        """
        self.alive = True
        self.thread = threading.Thread(target=self._comm_function)
        self.thread.start()
        
    def stop(self):
        """
        Stop the comm thread
        """
        self.alive = False
        self.thread.join()
        self.connected = False
        self.clientsocket.close()

    def connected(self):
        return self.connected

    def _comm_function(self):
        self.logger.info('Starting comm thread. %s:%d' % (self.server_address[0], self.server_address[1]))
        while self.alive:
            read_ok, lines = self.read_socket()
            if read_ok and self.callback_func != None:
                for line in lines:
                    #print("sending: %s" % line)
                    self.callback_func(line)
            else:
                time.sleep(0.05)
        self.logger.info('Finishing comm thread')

    def read_socket(self):
        lines = []
        if not self.connected:
            try:
                #self.logger.info("Connecting to server at %s:%d" % (self.server_address[0], self.server_address[1]))
                self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.clientsocket.connect(self.server_address)
                self.clientsocket.settimeout(1)
                self.connected = True
                self.logger.info("Connected to server at %s:%d" % (self.server_address[0], self.server_address[1]))
                self.buf = ''
            except socket.timeout:
                self.logger.debug("Socket timeout!")
                return False, lines
            except socket.error as e:
                #self.logger.error("Socket error! " + str(e) )
                return False, lines

        try:
            data = self.clientsocket.recv(1024)
        except socket.timeout as e:
            err = e.args[0]
            if err == 'timed out':
                #self.logger.error('recv timed out, retry later')
                return False, lines
            else:
                self.connected = False
                self.clientsocket.close()
                return False, lines
        except socket.error as e:
            self.logger.error("Socket error! " + str(e))
            self.connected = False
            self.clientsocket.close()
            return False, lines
        else:
            if len(data) == 0:
                self.logger.info('Server shut down...')
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
    logger = logging.getLogger("Callback")
    logger.info("Rec'd: " + msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client Socket class - Tester')
    parser.add_argument("port", type=int, help='Port on localhost to use')
    args = parser.parse_args()

    LOGGING = { 'version': 1, 'disable_existing_loggers': False,
        'formatters': { 'simple': { 'format': '%(asctime)s.%(msecs)03d [%(name)s] (%(levelname)s): %(message)s', "datefmt": "%Y-%m-%d %H:%M:%S"} },
        'handlers': { 'console': {'class': 'logging.StreamHandler', 'level':'DEBUG', 'formatter': 'simple'} },
        'root': {'handlers': ['console'],'level': 'DEBUG'}
    }
    logging.config.dictConfig(LOGGING)

    logger = logging.getLogger("client_socket")

    if args.port:
        port = args.port
    else:
        port = 5555
    
    c = ClientSocket('ClientSocket', ('127.0.0.1', port))
    logger.info("setting callback")
    c.setCallback(test_callback_func)
    logger.info("starting...")
    c.start()
    logger.info("waiting 0.5s")
    time.sleep(0.5)  # sleep a bit to allow reply

    msg = 'test 1'
    logger.info("sending msg: %s" % msg)
    c.write(msg)  # send cmd to server    
    logger.info("waiting 0.5s")
    time.sleep(0.5)  # sleep a bit to allow reply

    msg = 'test 2'
    logger.info("sending msg: %s" % msg)
    c.write(msg)  # send cmd to server    
    logger.info("waiting 0.5s")
    time.sleep(0.5)  # sleep a bit to allow reply

    msg = 'test 3'
    logger.info("sending msg: %s" % msg)
    c.write(msg)  # send cmd to server    
    logger.info("waiting 0.5s")
    time.sleep(0.5)  # sleep a bit to allow reply

    logger.info("shutting down...")
    c.stop()
