#!/usr/bin/env python

import os, sys

class MuninPlugin(object):
    graph_title = ""
    graph_args = None
    graph_vlabel = None
    graph_info = None
    graph_category = None
    fields = []

    def __init__(self):
        super(MuninPlugin, self).__init__()

    def autoconf(self):
        return False

    def config(self):
        conf = ["graph_title %s" % self.graph_title]
        for k in ('graph_category', 'graph_args', 'graph_vlabel', 'graph_info'):
            v = getattr(self, k)
            if v:
                conf.append('%s %s' % (k, v))

        for field_name, field_args in self.fields.iteritems():
            for arg_name, arg_value in field_args.iteritems():
                conf.append('%s.%s %s' % (field_name, arg_name, arg_value))

        print "\n".join(conf)

    def suggest(self):
        sys.exit(1)

    def run(self):
        cmd = (sys.argv[1] if len(sys.argv) > 1 else None) or "execute"
        if cmd == "execute":
            self.execute()
        elif cmd == "autoconf":
            if not self.autoconf():
                print "no"
            print "yes"
        elif cmd == "config":
            self.config()
        elif cmd == "suggest":
            self.suggest()
        sys.exit(0)

class MuninPostgresPlugin(MuninPlugin):
    dbname_in_args = False
    graph_category = "PostgreSQL"

    def __init__(self):
        super(MuninPostgresPlugin, self).__init__()

        self.dbname = ((sys.argv[0].rsplit('_', 1)[-1] if self.dbname_in_args else None)
            or os.environ.get('PGDATABASE') or 'template1')
        dsn = ["dbname='%s'" % self.dbname]
        for k in ('user', 'password', 'host'):
            v = os.environ.get('DB%s' % k.upper())
            if v:
                dsn.append("db%s='%s'" % (k, v))
        self.dsn = ' '.join(dsn)

    def connection(self):
        if not hasattr(self, '_connection'):
            import psycopg2
            self._connection = psycopg2.connect(self.dsn)
        return self._connection

    def cursor(self):
        return self.connection().cursor()

    def autoconf(self):
        return bool(self.connection())
