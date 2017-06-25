"""
bitwrap_io.api

this module provides an administrative API
  * for deploying PNML schemata as sql/pgsql entities
  * and for managing the creation of event streams

"""
from cyclone.jsonrpc import JsonrpcRequestHandler
import bitwrap_io
from bitwrap_io.api import headers
import bitwrap_io.storage.db as pg
from bitwrap_io.machine import pnml

class Handler(headers.Mixin, JsonrpcRequestHandler):
    """
    Operations for creating streams and installing database schemata
    """

    def jsonrpc_schema_create(self, schema):
        """
        test that an event-machine schema exists
        """
        machine = pnml.Machine(schema)
        pg.create_schema(machine, **self.settings)

        return self.jsonrpc_schema_exists(schema)

    def jsonrpc_schema_destroy(self, schema):
        """
        test that an event-machine schema exists
        """
        pg.drop_schema(schema, **self.settings)

    def jsonrpc_schema_exists(self, schema):
        """
        test that an event-machine schema exists
        """
        sm = bitwrap_io.open(schema, **self.settings)
        cur = sm.storage.db.cursor()

        cur.execute("""
        SELECT exists(select tablename from pg_tables where schemaname = '%s' and tablename = 'states');
        """ % schema)

        return cur.fetchone()[0]

    def jsonrpc_stream_exists(self, schema, oid):
        """
        test that a stream exists
        """
        sm = bitwrap_io.open(schema, **self.settings)
        cur = sm.storage.db.cursor()

        cur.execute("""
        SELECT exists(select oid FROM %s.states where oid = '%s');
        """ % (schema, oid))

        return cur.fetchone()[0]

    def jsonrpc_stream_create(self, schema, oid):
        """
        create a new stream if it doesn't exist 
        """
        sm = bitwrap_io.open(schema, **self.settings)
        cur = sm.storage.db.cursor()

        sql = """
        INSERT into %s.states (oid) values ('%s')
        """ % (schema, oid)

        return cur.execute(sql)
