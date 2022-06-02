#!/usr/bin/env python3

import socketserver
from queue import Queue
import threading
import time
import socket
import logging, logging.config

class SocketRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        buf = ""
        self.request.settimeout(0.05)
        while not self.done and self.server.client_cnt > 0:
            #line = self.rfile.readline().decode('utf-8').strip()
            #self.server.input_fifo.append(line)

            # first send out anything in the output fifo
            try:
                if not self.server.output_fifo.empty():
                    out_msg = self.server.output_fifo.get()
                    # print("Socket sending: %s" % out_msg)
                    self.request.send(out_msg)
            except NameError as e:
                self.server.logger.error("Exception:", exc_info=True)
                self.server.done = True
                break

            try:
                msg = self.request.recv(4096)
            except socket.timeout as e:
                err = e.args[0]
                # this next if/else is a bit redundant, but illustrates how the
                # timeout exception is setup
                if err == 'timed out':
                    #time.sleep(1)
                    #self.server.logger.error('recv timed out, retry later')
                    continue
                else:
                    print( e)
                    return
            except socket.error as e:
                # Something else happened, handle error, exit, etc.
                self.server.logger.error("Exception:", exc_info=True)
                return
            else:
                if len(msg) == 0:
                    self.server.logger.info( 'Client at %s disconnected' % (self.client_address,))
                    return
                else:
                    #print("rec'vd: %s" % msg.decode('utf-8'))
                    buf += msg.decode('utf-8')
                    idx = buf.find('\n')
                    while idx >= 0:
                        #self.server.input_fifo.put(buf[:idx])
                        #self.server.logger.debug("SocketRequestHandler: sending msg to callback: %s" % (buf[:idx]))
                        self.server.sendCallback(buf[:idx])
                        buf = buf[idx+1:]
                        idx = buf.find('\n')

        return

    def setup(self):
        self.server.logger.info("SocketRequestHandler setup, client address: %s" % (self.client_address,))
        self.done = False
        self.server.client_cnt += 1

    def finish(self):
        self.done = True
        self.server.client_cnt -= 1
        self.server.logger.info("SocketRequestHandler finish")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, name, server_address,
                 handler_class=SocketRequestHandler,
                 ):

        self.name = name
        self.callbackFuncion = None
        self.input_fifo = Queue()
        self.output_fifo = Queue()
        self.client_cnt = 0
        socketserver.TCPServer.allow_reuse_address = True
        socketserver.TCPServer.__init__(self, server_address,
                                        handler_class)

        # assumes logging has been previous configured...
        self.logger = logging.getLogger(self.name)

        self.logger.info("Created server at %s", (server_address,))

        return

    def setCallback(self, callbackFuncion):
        self.callbackFuncion=callbackFuncion
        self.logger.info("ThreadedTCPServer: callback func set")

    def sendCallback(self, cb_msg):
        if self.callbackFuncion is not None:
            self.callbackFuncion(cb_msg)
        else:
            self.input_fifo.put(cb_msg)

    def write(self, msg):
        if self.client_cnt > 0:
            self.output_fifo.put(('%s\n' % msg).encode('utf-8'))

    def start(self):
        # Start the server in a thread
        self.worker = threading.Thread(target=self.serve_forever)
        self.worker.setDaemon(True)  # don't hang on exit
        self.done = False
        self.worker.start()

    def stop(self):
        socketserver.TCPServer.shutdown(self)
        self.socket.close()
        self.client_cnt = 0
        #self.worker.join()

if __name__ == '__main__':
    '''
    Test code for ThreadedTCPServer.  Use netcat to test:

      $ echo "cmd1" | nc localhost 12888      # add "cmd1" to input fifo
      $ echo "cmd2" | nc localhost 12888      # add "cmd2" to input fifo
      $ echo "quit" | nc localhost 12888      # breaks out of process loop, shuts down
    '''
    import argparse

    parser = argparse.ArgumentParser(description='Server Socket class - Tester')
    parser.add_argument('-p', '--port', type=int, default=12888, help='Port on localhost to use', required=False)
    args = parser.parse_args()

    LOGGING = { 'version': 1, 'disable_existing_loggers': False,
        'formatters': { 'simple': { 'format': '%(asctime)s.%(msecs)03d [%(name)s] (%(levelname)s): %(message)s', "datefmt": "%Y-%m-%d %H:%M:%S"} },
        'handlers': { 'console': {'class': 'logging.StreamHandler', 'level':'DEBUG', 'formatter': 'simple'} },
        'root': {'handlers': ['console'],'level': 'DEBUG'}
    }
    logging.config.dictConfig(LOGGING)

    logger = logging.getLogger("main")

    # create the server, use port passed in as arg
    logger.info("Creating ThreadedTCPServer...")
    server = ThreadedTCPServer('Test_ThreadedTCPServer', ('localhost', args.port), SocketRequestHandler)

    # Start the server...
    server.start();

    logger.info("server started on localhost:%d.\nstarting process loop..." % (args.port))
    while True:
        if not server.input_fifo.empty():
            input_line = server.input_fifo.get()
            logger.info("processing input: %s" % (input_line))
            if input_line == 'quit':
                break
        else:
            time.sleep(0.01)
    logger.info("rec'd quit cmd, stopping loop...")

    # shutdown server...
    server.shutdown()
    logger.info("all shut down...")
