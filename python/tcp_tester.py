import socket
import time

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('127.0.0.1', 12070))

cmd_lst = ['{"method":"start"}\n', '{"method":"end"}\n']

cmd_num = 0
iter_cnt = 0
for i in range(0, 20000):
    iter_cnt += 1
    print("Starting iter %d" % (iter_cnt))
    clientsocket.send(cmd_lst[cmd_num])
    time.sleep(15)
    cmd_num = cmd_num ^ 1