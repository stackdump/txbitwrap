"""
bitwrap_io.storage.sql - statevector storage using postgresql

"""

import json
from bitwrap_io.storage.db import ProgrammingError, connect

_POOL = {}

class Storage(object):
    """ PGSQL Storage provider """

    def __init__(self, repo_name, state_machine, **kwargs):
        self.state_machine = state_machine

        if repo_name in _POOL:
            self.db = _POOL[repo_name]
        else:
            self.db = Datastore(self.state_machine, kwargs)
            _POOL[repo_name] = self.db

    def commit(self, req, dry_run=False):
        """ execute transition and persist to storage on success """

        curr = self.db.cursor()
        
        sql = """
        INSERT INTO %s.events(oid, action, payload)
          VALUES('%s', '%s', '%s')
          RETURNING to_json((hash, oid, seq )::%s.event) as event;
        """ % (self.db.schema, req['oid'], req['action'], req['payload'], self.db.schema)
        
        try:
            curr.execute(sql)
            res = curr.fetchone()

            if res:
                return res[0]

        except ProgrammingError:
            if (self.db.conn.error.args[3][:5] == 'value') :
                return { 'oid': req['oid'], '__err__': 'INVALID_OUTPUT' }
            else:
                return { 'oid': req['oid'], '__err__': 'INVALID_INPUT' }


class Datastore(object):
    """ store """

    def __init__(self, machine, rds_config):
        self.conn = connect(**rds_config)
        self.conn.autocommit = True

        self.schema = machine.name
        self.state = State(self)
        self.events = Events(self)
        self.state_machine = machine

    def cursor(self):
        """ open db transaction """
        return self.conn.cursor()

    def commit(self):
        """ commit txn """
        return self.conn.commit()

    def rollback(self):
        """ rollback txn """
        pass

# TODO: should possibly refactor sql to use string.Template
class State(object):
    """ Model """

    def __init__(self, store):

        self.store = store
        self.schema = self.store.schema

    def put(self, oid, vector=None, head=None):
        """ write """

        if head is None:
            head = 'null'
        else:
            head = '"' + head + '"'

        body = json.dumps(vector)
        sql = """
        UPDATE bitwrap.state SET vector = "%s", head = %s
        WHERE oid = "%s" AND schema = "%s"
        """

        res = self.store.conn.execute(sql % (body, head, oid, self.schema))

        if res == 0:
            sql = """
            INSERT INTO bitwrap.state
            VALUES ("%s", "%s", "%s", %s)
            """
            res = self.store.conn.execute(sql % (self.schema, oid, body, head))

        return res

    def head(self, oid):
        """ read head """

        sql = """
        SELECT head FROM bitwrap.state
        WHERE oid = "%s" AND schema = "%s"
        """

        res = self.store.conn.execute(sql % (oid, self.schema))

        if res == 0:
            return None
        else:
            return self.store.conn.fetchone()[0]

    def vector(self, oid):
        """ get state vector """

        sql = """
        SELECT state FROM %s_states WHERE oid = '%s'
        """ % (self.schema, oid)

        cursor = self.store.conn.cursor()
        cursor.execute(sql)
        res = cursor.fetchone()

        if res is None:
            return self.store.state_machine.machine['state']
        else:
            # FIXME return the actual value
            ##rec = self.store.conn.fetchone()
            pass

    def get(self, oid):
        """ get state record"""

        sql = """
        SELECT oid, vector, head FROM bitwrap.state
        WHERE oid = "%s" AND schema = "%s"
        """

        res = self.store.conn.execute(sql % (oid, self.schema))
        if res == 0:
            return {
                'oid': oid,
                'vector': self.store.state_machine.machine['state'],
                'head': None,
                'schema': self.schema
            }
        else:
            rec = self.store.conn.fetchone()

            return {
                'oid': rec[0],
                'vector': json.loads(rec[1]),
                'head': rec[2],
                'schema': self.schema
            }

class Events(object):
    """ Model """

    def __init__(self, store):
        self.store = store
        self.schema = self.store.schema

    def put(self, eventid, body, prev):
        """ write event """
        oid = body.get('oid', None)
        body = base64.b64encode(json.dumps(body))

        sql = """
        INSERT INTO bitwrap.events( oid, schema, eventid, body, previous)
        VALUES ( "%s", "%s", "%s", "%s", "%s")
        """
        return self.store.conn.execute(sql % (oid, self.schema, eventid, body, prev))

    def get(self, eventid):
        """ get event by id """

        sql = """
        SELECT body, id FROM bitwrap.events
        WHERE eventid = "%s" and schema = "%s"
        """

        res = self.store.conn.execute(sql % (eventid, self.schema))
        if res == 0:
            return {'id': None, 'event': {}, 'schema': self.schema, 'seq': None}
        else:
            rec = self.store.conn.fetchone()

            return {
                'id': eventid,
                'event': json.loads(base64.b64decode(rec[0])),
                'schema': self.schema,
                'seq': rec[1]
            }

    def list(self, oid):
        """ read complete stream """

        sql = """
        SELECT body, eventid, id FROM bitwrap.events
        WHERE oid = "%s" and schema = "%s" ORDER BY id DESC
        """

        res = self.store.conn.execute(sql % (oid, self.schema))
        if res == 0:
            return {'events': []}
        else:
            result = []
            for rec in self.store.conn.fetchall():
                evt = json.loads(base64.b64decode(rec[0]))
                evt['id'] = rec[1]
                evt['seq'] = rec[2]
                result.append(evt)

            return {'events': result, 'oid': oid, 'schema': self.schema}
