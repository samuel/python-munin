#!/usr/bin/env python

import os
import socket
import SocketServer
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
    p = Popen([path] + ([cmd] if cmd else []), stdout=PIPE)
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
            plugin = cmd[1] if len(cmd) > 1 else None

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
                out = execute_plugin(os.path.join(self.server.options.plugin_path, plugin), "config" if cmd[0] == "config" else "")
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
    server = MuninServer((HOST, PORT), MuninRequestHandler, bind_and_activate=False)
    server.allow_reuse_address = True
    server.server_bind()
    server.server_activate()
    ip, port = server.server_address
    options, args = parse_args()
    options.plugin_path = os.path.abspath(options.plugin_path)
    server.options = options
    server.serve_forever()

"""
# munin node at chatter1
list
space separated list of plugins

help
# Unknown command. Try list, nodes, config, fetch, version or quit

nodes
chatter1
.

config
# Unknown service
.

config open_inodes
graph_title Inode table usage
graph_args --base 1000 -l 0
graph_vlabel number of open inodes
graph_category system
graph_info This graph monitors the Linux open inode table.
used.label open inodes
used.info The number of currently open inodes.
max.label inode table size
max.info The size of the system inode table. This is dynamically adjusted by the kernel.
.

fetch open_inodes
used.value 25034
max.value 45497
.

version
munins node on chatter1 version: 1.2.6
"""
