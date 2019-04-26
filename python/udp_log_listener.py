import sys
import socket

def main(argv):
    argc = len(argv)
    if argc == 1:
        print("usage:\n  udp_log_listener IP_ADDRESS [PORT]")
        sys.exit()
    elif argc == 2:
        UDP_IP = argv[1]
        UDP_PORT = 8080
    elif argc == 3:
        UDP_IP = argv[1]
        UDP_PORT = int(argv[2])

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    print("Starting udp listener on %s:%d" % (UDP_IP, UDP_PORT))
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print("(%s): %s" % (addr, data))

if __name__ == '__main__':
  main(sys.argv)
