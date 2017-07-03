"""
bitwrap_io.api

this module provides an administrative API
  * for deploying PNML schemata as sql/pgsql entities
  * and for managing the creation of event streams

"""
from cyclone.jsonrpc import JsonrpcRequestHandler
import bitwrap_io
from bitwrap_io.api import headers
import bitwrap_psql.db as pg
import bitwrap_machine as pnml

class Handler(headers.Mixin, JsonrpcRequestHandler):
    """ Operations for creating streams and installing database schemata """

    def handle(self, schema):
        """ open handle on bitwrap storage """
        return bitwrap_io.open(schema, **self.settings)

    def jsonrpc_schema_exists(self, schema):
        """ test that an event-machine schema exists """
        return self.handle(schema).storage.db.schema_exists()

    def jsonrpc_schema_create(self, schema):
        """ test that an event-machine schema exists """
        machine = pnml.Machine(schema)
        try:
            pg.create_schema(machine, **self.settings)
        except:
            pass

        return self.jsonrpc_schema_exists(schema)

    def jsonrpc_schema_destroy(self, schema):
        """ test that an event-machine schema exists """
        pg.drop_schema(schema, **self.settings)


    def jsonrpc_stream_exists(self, schema, oid):
        """ test that a stream exists """
        return self.handle(schema).storage.db.stream_exists(oid)


    def jsonrpc_stream_create(self, schema, oid):
        """ create a new stream if it doesn't exist """
        return self.handle(schema).storage.db.create_stream(oid)
