"""
Test EventStore Remote Procedure calls
"""
import time
from twisted.internet import defer
from txbitwrap.test import ApiTest
import bitwrap_psql.db as pg
import bitwrap_machine as pnml


class RpcApiTest(ApiTest):
    """ Test ops for eventstore config and management """

    cli = ApiTest.client('api')

    def test_eventstore_db_schemata_admin(self):
        """ test write operation using a sequence of tic-tac-toe events """

        d = defer.Deferred()
        oid = 'trial-' + time.time().__str__()
        schema = 'octoe'
        machine = pnml.Machine(schema)
        pg.recreate_db(**self.options)
        pg.create_schema(pnml.Machine(schema), drop=True, **self.options)

        def create_stream(stream_already_exists):
            self.assertFalse(stream_already_exists)
            return self.cli.stream_create(schema, oid)

        def schema_exists(_):
            return self.cli.schema_exists(schema)

        def stream_exists(schema_exists):
            self.assertTrue(schema_exists)
            return self.cli.stream_exists(schema, oid)

        def schema_destroy(_):
            return self.cli.schema_destroy(schema)

        def assert_destroyed(schema_exists):
            self.assertFalse(schema_exists)

        def schema_create(_):
            return self.cli.schema_create(schema)

        def assert_created(schema_exists):
            self.assertTrue(schema_exists)

        d.addCallback(schema_exists)
        d.addCallback(stream_exists)
        d.addCallback(create_stream)
        d.addCallback(schema_destroy)

        d.addCallback(schema_exists)
        d.addCallback(assert_destroyed)
        d.addCallback(schema_create)
        d.addCallback(assert_created)

        d.callback(None)

        return d
