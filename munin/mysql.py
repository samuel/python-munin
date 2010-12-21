
import os, sys
from munin import MuninPlugin

class MuninMySQLPlugin(MuninPlugin):
    dbname_in_args = False
    category = "MySQL"

    def __init__(self):
        super(MuninMySQLPlugin, self).__init__()

        self.dbname = ((sys.argv[0].rsplit('_', 1)[-1] if self.dbname_in_args else None)
            or os.environ.get('DATABASE') or self.default_table)

        self.conninfo = dict(
            user = "root",
            host = "localhost",
        )

        for k in ('user', 'passwd', 'host', 'port'):
            v = os.environ.get(k)
            if v:
                self.conninfo[k] = v

    def connection(self):
        if not hasattr(self, '_connection'):
            import MySQLdb
            self._connection = MySQLdb.connect(**self.conninfo)
        return self._connection

    def cursor(self):
        return self.connection().cursor()

    def autoconf(self):
        return bool(self.connection())
