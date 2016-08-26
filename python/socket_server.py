import socketserver
import argparse

class EchoHandler(socketserver.BaseRequestHandler):
    def handle(self):
        cnt = 0
        while True:
            data = self.request.recv(1024)
            if not data:
                print(' -- Detected Disconnection -- ')
                break
            msg = data.decode('utf-8').replace('\n', '')
            #print("Rec'd raw: " + str(data))
            print("Rec'd: %s" % msg)
            cnt += 1
            self.request.sendall(('echo[%d]: %s\n' % (cnt, msg)).encode('utf-8'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple Socket: displays input then echos back')
    parser.add_argument("port", type=int, help='Port on localhost to use')
    args = parser.parse_args()

    if args.port:
        port = args.port
    else:
        port = 5555

    server = socketserver.TCPServer(('localhost', port), EchoHandler)
    server.allow_reuse_address = True
    print("Server socket listening on localhost:%d" % port)
    server.serve_forever()

