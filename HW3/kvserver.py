#!/usr/bin/env python
from __future__ import print_function

import sys
import json

try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from http.server import BaseHTTPRequestHandler, HTTPServer
sys.path.append("../")
from pysyncobj import SyncObj, SyncObjConf, replicated


class KVStorage(SyncObj):
    def __init__(self, selfAddress, partnerAddrs, dumpFile):
        conf = SyncObjConf(
            fullDumpFile=dumpFile,
        )
        super(KVStorage, self).__init__(selfAddress, partnerAddrs, conf)
        self.__data = {}

    @replicated
    def set(self, key, value):
        self.__data[key] = value

    @replicated
    def pop(self, key):
        self.__data.pop(key, None)

    def get(self, key):
        return self.__data.get(key, None)

    def get_all(self):
        return self.__data

    def get_leader(self):
        return self._getLeader()

_g_kvstorage = None

def handle_unserializable(obj):
    try:
        json.dumps(obj)
    except TypeError:
        return None
    return obj

class KVRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if _g_kvstorage.get_leader() is None:
            self.send_response(500)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            return
        try:
            path = self.path
            if path == '/status':
                status = _g_kvstorage.getStatus()
                status['self'] = status['self'].address
                status['leader'] = status['leader'].address
                json_data = json.dumps(status, default=handle_unserializable)

                self.send_response(200)
                self.send_header("Content-type", "text/json")
                self.end_headers()

                self.wfile.write(json_data.encode('utf-8'))
                return
            if path == '/':
                data = _g_kvstorage.get_all()

                json_data = json.dumps(data)

                self.send_response(200)
                self.send_header("Content-type", "text/json")
                self.end_headers()

                self.wfile.write(json_data.encode('utf-8'))
                return

            value = _g_kvstorage.get(path)
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(value.encode('utf-8'))
            self.wfile.write('\n'.encode('utf-8'))
            self.wfile.write(("Leader is : " + _g_kvstorage.get_leader().address).encode('utf-8'))
        except:
            pass

    def do_POST(self):
        if _g_kvstorage.get_leader() is None:
            self.send_response(500)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            return
        try:
            key = self.path
            value = self.rfile.read(int(self.headers.get('content-length'))).decode('utf-8')
            _g_kvstorage.set(key, value)
            self.send_response(201)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(("Leader is : " + _g_kvstorage.get_leader().address).encode('utf-8'))
        except:
            pass


def main():
    if len(sys.argv) < 5:
        print('Usage: %s http_port dump_file.bin selfHost:port partner1Host:port partner2Host:port ...' % sys.argv[0])
        sys.exit(-1)

    httpPort = int(sys.argv[1])
    dumpFile = sys.argv[2]
    selfAddr = sys.argv[3]
    partners = sys.argv[4:]

    global _g_kvstorage
    _g_kvstorage = KVStorage(selfAddr, partners, dumpFile)
    httpServer = HTTPServer(('', httpPort), KVRequestHandler)
    httpServer.serve_forever()


if __name__ == '__main__':
    main()
