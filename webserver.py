from __future__ import print_function
import SimpleHTTPServer
import SocketServer
import sys


class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        self.do_GET()


if __name__ == "__main__":
    host = '0.0.0.0'
    port = 8000

    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    elif len(sys.argv) > 2:
        host = sys.argv[1]
        port = int(sys.argv[2])

    server = SocketServer.TCPServer((host, port), ServerHandler)
    server.serve_forever()