""" admin api to allow management of streams and event schemata """
from cyclone.jsonrpc import JsonrpcRequestHandler
from txbitwrap.api import headers
import txbitwrap
import bitwrap_machine as pnml
import bitwrap_psql.db as pg

class Rpc(headers.Mixin, JsonrpcRequestHandler):
    """ Operations for creating streams and installing database schemata """

    def handle(self, schema):
        """ open handle on bitwrap storage """
        return txbitwrap.open(schema, **self.settings)

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
        """ drop database schema """
        pg.drop_schema(schema, **self.settings)


    def jsonrpc_stream_exists(self, schema, oid):
        """ test that a stream exists """
        return self.handle(schema).storage.db.stream_exists(oid)


    def jsonrpc_stream_create(self, schema, oid):
        """ create a new stream if it doesn't exist """
        return self.handle(schema).storage.db.create_stream(oid)
