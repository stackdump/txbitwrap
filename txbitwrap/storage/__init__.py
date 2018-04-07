"""
provides stateful event storage using postgresql
"""

from string import Template
from txbitwrap.storage.postgres import ProgrammingError, connect
from twisted.internet import defer
import psycopg2

_DB = {}

# TODO: after refactor to use adbapi adapter 
# relocate these classes to txbitwrap/storage/postgres/__init__.py
# this module should provide a factory method for returning storage
class Storage(object):
    """ PGSQL Storage provider """

    def __init__(self, schema, **kwargs):
        global _DB

        if schema in _DB:
            self.db = _DB[schema]
        else:
            self.db = Database(schema, kwargs)
            _DB[schema] = self.db

    def commit(self, req):
        """ execute transition and persist to storage on success """

        if req['payload'] == '':
            req['payload'] = '{}'

        res = defer.Deferred()

        sql = """
        INSERT INTO %s.events(oid, action, payload)
          VALUES('%s', '%s', '%s')
        RETURNING
          to_json((hash, oid, seq )::%s.event) as event;
        """ % (self.db.schema, req['oid'], req['action'], req['payload'], self.db.schema)

        d = self.db.conn.runQuery(sql)

        def _pass(reply):
            res.callback(reply[0][0])

        def _fail(failure):
            #print failure
            if failure.type == psycopg2.IntegrityError:
                req['__err__'] = 'CONFLICT'
            else:
                req['__err__'] = 'INVALID'

            res.callback(req)

        d.addCallback(_pass)
        d.addErrback(_fail)
        return res


class Database(object):
    """ store """

    def __init__(self, schema, rds_config):
        self.conn = connect(**rds_config)

        self.schema = schema
        self.states = States(self)
        self.events = Events(self)

    def schema_exists(self):
        """
        test that an event-machine schema exists
        """
        d = self.conn.runQuery("""
        select exists(SELECT schema_name FROM information_schema.schemata WHERE schema_name = '%s');
        """ % self.schema)

        d.addCallback(lambda res: res[0][0])

        return d

    def stream_exists(self, oid):
        """
        test that a stream exists
        """
        sql = """
        SELECT exists(select oid FROM %s.states where oid = '%s');
        """ % (self.schema, oid)

        d = self.conn.runQuery(sql)
        d.addCallback(lambda res: res[0][0])

        return d

    def create_stream(self, oid):
        """
        create a new stream if it doesn't exist 
        """
        d = self.conn.runOperation("""
        INSERT into %s.states (oid) values ('%s')
        """ % (self.schema, oid))

        return d

class States(object):
    """ Model """

    def __init__(self, db):
        self.db = db

    def fetch(self, key):
        """ get event by eventid """

        tpl = Template("""
        SELECT
          to_json((ev.hash, st.oid, ev.action, st.rev, st.state, ev.payload, modified, created)::${name}.current_state)
        FROM
          ${name}.states st
        LEFT JOIN
          ${name}.events ev ON ev.oid = st.oid AND ev.seq = st.rev
        WHERE
          st.oid = '${oid}'
        """)

        sql = tpl.substitute(
            name=self.db.schema,
            oid=key
        )

        d = self.db.conn.runQuery(sql)
        d.addCallback(lambda res: res[0][0])

        return d

class Events(object):
    """ Model """

    def __init__(self, db):
        self.db = db

    def fetch(self, key):
        """ get event by eventid """

        sql = """
        SELECT
            row_to_json((hash, oid, seq, action, payload, timestamp)::%s.event_payload)
        FROM
            %s.events
        WHERE
            hash = '%s'
        ORDER BY seq DESC
        """  % (self.db.schema, self.db.schema, key)

        d = self.db.conn.runQuery(sql)
        d.addCallback(lambda res: res[0][0])
        return d

    def fetchall(self, key):

        sql = """
        SELECT
            row_to_json((hash, oid, seq, action, payload, timestamp)::%s.event_payload)
        FROM
            %s.events
        WHERE
            oid = '%s'
        ORDER BY seq DESC
        """  % (self.db.schema, self.db.schema, key)

        def _unpack(rows):
            reply = [row[0] for row in rows]
            return reply

        d = self.db.conn.runQuery(sql)
        d.addCallback(_unpack)
        return d
