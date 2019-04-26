#!/usr/bin/env python3

import socketserver
from queue import Queue
import threading
import time
import socket

class SocketRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        buf = ""
        self.request.settimeout(0.05)
        self.done = False
        while not self.done:
            #line = self.rfile.readline().decode('utf-8').strip()
            #self.server.input_fifo.append(line)

            # first send out anything in the output fifo
            try:
                if not self.server.output_fifo.empty():
                    out_msg = self.server.output_fifo.get()
                    self.request.send(out_msg)
            except NameError as e:
                print( e)
                self.done = True
                break

            try:
                msg = self.request.recv(4096)
            except socket.timeout as e:
                err = e.args[0]
                # this next if/else is a bit redundant, but illustrates how the
                # timeout exception is setup
                if err == 'timed out':
                    #time.sleep(1)
                    #print('recv timed out, retry later')
                    continue
                else:
                    print( e)
                    return
            except socket.error as e:
                # Something else happened, handle error, exit, etc.
                print( e)
                return
            else:
                if len(msg) == 0:
                    print( 'Client at %s disconnected' % (self.client_address,))
                    return
                else:
                    #print("rec'vd: %s" % msg.decode('utf-8'))
                    buf += msg.decode('utf-8')
                    idx = buf.find('\n')
                    while idx >= 0:
                        #self.server.input_fifo.put(buf[:idx])
                        #print("SocketRequestHandler: sending msg to callback: %s" % (buf[:idx]))
                        self.server.sendCallback(buf[:idx])
                        buf = buf[idx+1:]
                        idx = buf.find('\n')

        return

    def setup(self):
        print("SocketRequestHandler setup, client address: %s" % (self.client_address,))

    def finish(self):
        self.done = True
        print("SocketRequestHandler finish")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address,
                 handler_class=SocketRequestHandler,
                 ):
        self.callbackFuncion = None
        self.input_fifo = Queue()
        self.output_fifo = Queue()
        socketserver.TCPServer.__init__(self, server_address,
                                        handler_class)
        return

    def setCallback(self, callbackFuncion):
        self.callbackFuncion=callbackFuncion
        print ("ThreadedTCPServer: callback func set")

    def sendCallback(self, cb_msg):
        if self.callbackFuncion is not None:
            self.callbackFuncion(cb_msg)

    def write(self, msg):
        self.output_fifo.put(('%s\n' % msg).encode('utf-8'))

    def start(self):
        # Start the server in a thread
        self.worker = threading.Thread(target=self.serve_forever)
        self.worker.setDaemon(True)  # don't hang on exit
        self.worker.start()

    def stop(self):
        socketserver.TCPServer.shutdown(self)
        self.socket.close()
        self.worker.join()

if __name__ == '__main__':
    '''
    Test code for ThreadedTCPServer.  Use netcat to test:

      $ echo "cmd1" | nc localhost 12888      # add "cmd1" to input fifo
      $ echo "cmd2" | nc localhost 12888      # add "cmd2" to input fifo
      $ echo "quit" | nc localhost 12888      # breaks out of process loop, shuts down
    '''
    import argparse

    parser = argparse.ArgumentParser(description='Server Socket class - Tester')
    parser.add_argument('--port', type=int, default=12888, help='Port to use (def: 12888)', required=False)
    parser.add_argument('--ip', type=str, default='localhost', help='IP address (def: localhost)', required=False)
    args = parser.parse_args()

    # create the server, use port passed in as arg
    server = ThreadedTCPServer((args.ip, args.port), SocketRequestHandler)

    # Start the server...
    server.start();

    print("server started on %s:%d.\nstarting process loop..." % (args.ip, args.port))
    while True:
        if not server.input_fifo.empty():
            input_line = server.input_fifo.get()
            print("processing input: %s" % (input_line))
            if input_line == 'quit':
                break
        else:
            time.sleep(0.01)
    print("rec'd quit cmd, stopping loop...")

    # shutdown server...
    server.shutdown()
    print("all shut down...")
