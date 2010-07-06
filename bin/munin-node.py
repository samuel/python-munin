#!/usr/bin/env python

import os
import socket
import SocketServer
import sys
import threading
import time
from subprocess import Popen, PIPE

PLUGIN_PATH = "/etc/munin/plugins"

def parse_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p", "--pluginpath", dest="plugin_path",
                      help="path to plugins", default=PLUGIN_PATH)
    (options, args) = parser.parse_args()
    return options, args


def execute_plugin(path, cmd=""):
    args = [path]
    if cmd:
        args.append(cmd)
    p = Popen(args, stdout=PIPE)
    output = p.communicate()[0]
    return output

class MuninRequestHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        plugins = os.listdir(self.server.options.plugin_path)
        node_name = socket.gethostname().split('.')[0]
        self.wfile.write("# munin node at %s\n" % node_name)
        while True:
            line = self.rfile.readline()
            if not line:
                break
            line = line.strip()

            cmd = line.split(' ', 1)
            plugin = (len(cmd) > 1) and cmd[1] or None

            if cmd[0] == "list":
                self.wfile.write("%s\n" % " ".join(plugins))
            elif cmd[0] == "nodes":
                self.wfile.write("nodes\n%s\n.\n" % (node_name))
            elif cmd[0] == "version":
                self.wfile.write("munins node on chatter1 version: 1.2.6\n")
            elif cmd[0] in ("fetch", "config"):
                if plugin not in plugins:
                    self.wfile.write("# Unknown service\n.\n")
                    continue
                c = (cmd[0] == "config") and "config" or ""
                out = execute_plugin(os.path.join(self.server.options.plugin_path, plugin), c)
                self.wfile.write(out)
                if out and out[-1] != "\n":
                    self.wfile.write("\n")
                self.wfile.write(".\n")
            else:
                self.wfile.write("# Unknown command. Try list, nodes, config, fetch, version or quit\n")


class MuninServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 4949
    if sys.version_info[:3] >= (2, 6, 0):
        server = MuninServer((HOST, PORT), MuninRequestHandler, bind_and_activate=False)
        server.allow_reuse_address = True
        server.server_bind()
        server.server_activate()
    else:
        server = MuninServer((HOST, PORT), MuninRequestHandler)
    ip, port = server.server_address
    options, args = parse_args()
    options.plugin_path = os.path.abspath(options.plugin_path)
    server.options = options
    server.serve_forever()
