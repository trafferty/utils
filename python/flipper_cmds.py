#!/usr/bin/env python
import time
import sys
import socket
import logging

HOST = '192.168.0.22'  
PORT = 200

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

def connect(host=HOST, port=PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect( (host, port) )
    except socket.error:
        logging.error(f"Error connecting to {host}:{port}")
        return None
    return sock

def sendMsg(sock, msg):
    msg += '\r\n'
    send_buf = msg.encode()
    sock.sendall(send_buf)
    time.sleep(0.005)
    res_buf = sock.recv(256).decode("utf-8")
    if '\n' not in res_buf:
        logging.warn("Second try...")
        time.sleep(0.01)
        res_buf += self.xpm_sock.recv(256).decode("utf-8")
    return res_buf.strip()
    
def sendMsgP(sock, msg):
    logging.info("Send: " + msg)
    resp = sendMsg(sock, msg)
    if len(resp) > 0:
        logging.info("Rcv'd: " + resp)
        return processResp(resp)
    else:
        logging.error("no reply")
        return False

def processResp(resp):
    cmd, errorCode, *args = resp.strip().replace(' ', '').split(',')
    errStr = translateErrorCode(int(errorCode))
    print(f"[{cmd}]-> {errStr}")
    if len(args) > 0:
        if cmd == 'INIT':
            print(f" Wafer present: {args[0]}")
        elif cmd == 'STAT':
            print(f" Init OK: {args[0]}")
            print(f" Busy: {args[1]}")
            print(f" Wafer present: {args[2]}")
            print(f" Jaws Open: {args[3]}")
            print(f" Flip Orientation: {args[4]}")
        elif cmd == 'VER':
            print(f" SW Version: {args[0]}")
        elif cmd == 'SENSEWAFER':
            print(f" Wafer present: {args[0]}")
        elif cmd == 'OPEN':
            print(f" Wafer present: {args[0]}")
        elif cmd == 'CLOSE':
            print(f" Wafer present: {args[0]}")
        elif cmd == 'FLIP':
            print(f" Orientation: {args[0]}")
    if int(errorCode) == 1:
        return True
    else:
        return False

def translateErrorCode(errorCode):
    errStrs = [
        'Successful',
        'Unknown: -1',
        'Unrecognized command',
        'Unknown: -3',
        'Invalid number of arguments',
        'Unknown: -5',
        'Unknown: -6',
        'Motor error',
        'Unknown: -8',
        'System interlock fault',
        'Can\'t flip while gripper opened',
        'Skewed wafer',
        'Flipper busy',
        'Gripper close sensor not detected',
        'Gripper open sensor not detected',
        'Flipper not initialized',
        'Gripper motor failure']

    if errorCode == 1:
        return errStrs[0]
    elif errorCode < 0 and errorCode > -16:
        return errStrs[-1*errorCode]
    else:
        return f'Unknown error code: {errorCode}'

def repeat(sock, msg, cnt, delay_s=1.0):
    for i in range(cnt):
        sendMsgP(sock, msg)
        time.sleep(delay_s)

def cycle(sock, num_cycles):
    cmds = ["OPEN", "CLOSE", "FLIP, U", "OPEN", "CLOSE", "FLIP, D",]
    #cmds = ["FLIP, U", "FLIP, D",]
    for n in range(num_cycles):
        logging.info(f"\n*******************************\nStarting cycle {n+1} of {num_cycles}\n")
        for cmd in cmds:
            success = sendMsgP(sock, cmd)
            if not success:
                logging.error("Error with cycle cmd")
                return False
            #time.sleep(0.5)
    return True

if __name__ == "__main__":
    logging.info(f"Connecting to flipper at {HOST}:{PORT}...")
    sock = connect(HOST, PORT)
    if sock is None:
        logging.error("Could not connect. Check flipper power?")
        sys.exit()
    logging.info("Connected to flipper.")

    cmd_list = ['INIT', 'JOG', 'REC', 'OPEN', 'CLOSE', 'FLIP', 'SENSEWAFER', 'VER', 'STAT']
    while True:
        cmd = input("\n>>> ")
        if cmd.isnumeric():
            idx = int(cmd)
            if idx < len(cmd_list) and idx >= 0:
                logging.info(f"Sending cmd: {cmd_list[idx]}")
                sendMsgP(sock, cmd_list[idx])
            else:
                logging.error(f"Command index out of range: {idx}")
        elif len(cmd.split(' ')) > 1:
            cmd_pieces = cmd.split(' ')
            if (cmd_pieces[0] == 'rep' or cmd_pieces[0] == 'repeat') and len(cmd_pieces) == 4:
                cmd = cmd_pieces[1]
                cnt = int(cmd_pieces[2])
                delay_s = float(cmd_pieces[3])
                repeat(sock, cmd.upper(), cnt, delay_s=1.0)
            elif cmd_pieces[0] == 'cycle' and len(cmd_pieces) == 2:
                num_cycles = int(cmd_pieces[1])
                cycle(sock, num_cycles)
            else:
                sendMsgP(sock, cmd.upper())
        elif cmd == 'q' or cmd == 'quit':
            break
        elif cmd == 'q' or cmd == 'quit':
            break
        elif cmd == '?' or cmd == 'help':
            print("-----------------------\nCommand List:")
            for i,c in enumerate(cmd_list):
                print(f"  {i}: {c}")
            print("  repeat cmd: rep cmd cnt delay_s")
            print("-----------------------")
        else:
            sendMsgP(sock, cmd.upper())
    sock.close()
