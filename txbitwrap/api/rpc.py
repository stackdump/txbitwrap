""" admin api to allow management of streams and event schemata """
from cyclone.jsonrpc import JsonrpcRequestHandler
from txbitwrap.event.dispatch import Dispatcher
from txbitwrap.api import headers
import txbitwrap
import bitwrap_machine as pnml
import bitwrap_psql.db as pg


class Rpc(headers.Mixin, JsonrpcRequestHandler):
    """ Operations for creating streams and installing database schemata """

    def handle(self, schema):
        """ open handle on bitwrap storage """
        return txbitwrap.storage(schema, **self.settings)

    def jsonrpc_schema_exists(self, schema):
        """ test that an event-machine schema exists """
        return self.handle(schema).storage.db.schema_exists()

    def jsonrpc_schema_create(self, machine_name, schema):
        """ load state machine as database schema optionally specify a schema name """
        if schema is None:
            name = machine_name
        else:
            name = schema

        pg.create_schema(pnml.Machine(machine_name), schema_name=name, **self.settings)

        return self.jsonrpc_schema_exists(name)

    def jsonrpc_schema_destroy(self, schema):
        """ drop database schema """
        pg.drop_schema(schema, **self.settings)

    def jsonrpc_stream_exists(self, schema, oid):
        """ test that a stream exists """
        return self.handle(schema).storage.db.stream_exists(oid)

    def jsonrpc_stream_create(self, schema, oid):
        """ create a new stream if it doesn't exist """
        return self.handle(schema).storage.db.create_stream(oid)
