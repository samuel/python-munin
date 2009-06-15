
import sys

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

        for field_name, field_args in self.fields:
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
            try:
                ac = self.autoconf()
            except Exception, exc:
                print "no (%s)" % str(exc)
                sys.exit(1)
            if not ac:
                print "no"
                sys.exit(1)
            print "yes"
        elif cmd == "config":
            self.config()
        elif cmd == "suggest":
            self.suggest()
        sys.exit(0)
