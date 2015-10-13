import socket
import time
import threading

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('127.0.0.1', 12070))

def read_socket():
    while True:
        line = clientsocket.recv(1024)
        print line,
        time.sleep(.01)


_thread = threading.Thread(target=read_socket)
_thread.setDaemon(1)
_thread.start()

cmd_lst = ['{"method":"start"}\n', '{"method":"end"}\n']

cmd_num = 0
iter_cnt = 0
for i in range(0, 20000):
    iter_cnt += 1
    print("Starting iter %d" % (iter_cnt))
    clientsocket.send(cmd_lst[cmd_num])
    time.sleep(8)
    cmd_num = cmd_num ^ 1
