""" admin api to allow management of streams and event schemata """
from cyclone.jsonrpc import JsonrpcRequestHandler
from txbitwrap.event.dispatch import Dispatcher
from txbitwrap.api import headers
import txbitwrap
import txbitwrap.machine as pnml
import txbitwrap.storage.postgres as pgsql


class Rpc(headers.Mixin, JsonrpcRequestHandler):
    """ Operations for creating streams and installing database schemata """

    def handle(self, schema):
        """ open handle on bitwrap storage """
        return txbitwrap.eventstore(schema, **self.settings)

    def jsonrpc_schema_exists(self, schema):
        """ test that an event-machine schema exists """
        return self.handle(schema).storage.db.schema_exists()

    def jsonrpc_schema_create(self, machine_name, schema):
        """ load state machine as database schema optionally specify a schema name """
        if schema is None:
            name = machine_name
        else:
            name = schema

        d = pgsql.create_schema(pnml.Machine(machine_name), schema_name=name, **self.settings)
        d.addCallback(lambda _: self.jsonrpc_schema_exists(name))
        return d

    def jsonrpc_schema_destroy(self, schema):
        """ drop database schema """
        pgsql.drop_schema(schema, **self.settings)

    def jsonrpc_stream_exists(self, schema, oid):
        """ test that a stream exists """
        return self.handle(schema).storage.db.stream_exists(oid)

    def jsonrpc_stream_create(self, schema, oid):
        """ create a new stream if it doesn't exist """
        return self.handle(schema).storage.db.create_stream(oid)
