#!/usr/bin/env python
import time
import sys
from pyreadline import Readline
import socket

HOST = '192.168.0.22'  
PORT = 200

def connect(host=HOST, port=PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect( (host, port) )
    except socket.error:
        print(f"Error connecting to {host}:{port}")
        return None
    return sock

def sendMsg(sock, msg):
    msg += '\r\n'
    send_buf = msg.encode()
    sock.sendall(send_buf)
    time.sleep(0.005)
    res_buf = sock.recv(256).decode("utf-8")
    if '\n' not in res_buf:
        print("Second try...")
        time.sleep(0.01)
        res_buf += self.xpm_sock.recv(256).decode("utf-8")
    return res_buf.strip()
    
def sendMsgP(sock, msg):
    recv = sendMsg(sock, msg)
    if len(recv) > 0:
        print("Rcv'd: " + recv)
    else:
        print("no reply")

class SimpleCompleter(object):
    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response

if __name__ == "__main__":
    print(f"Connecting to flipper at {HOST}:{PORT}")
    sock = connect(HOST, PORT)
    if sock is None:
        print("Check flipper power?")
        sys.exit()

    cmd_list = ['INIT', 'JOG', 'REC', 'OPEN', 'CLOSE', 'FLIP', 'SENSEWAFER', 'VER', 'STAT']
    readline = Readline()

    # Register our completer function
    readline.set_completer(SimpleCompleter(cmd_list).complete)
    # Use the tab key for completion
    readline.parse_and_bind('tab: complete')

    while True:
        cmd = input("\n>>> ")
        if cmd == 'q' or cmd == 'quit':
            break
        else:
            sendMsgP(sock, cmd.upper())
