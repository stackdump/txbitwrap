"""
Test EventStore Remote Procedure calls
"""
import time
from twisted.internet import defer
from txbitwrap.test import ApiTest
import txbitwrap.storage.postgres as psql
import txbitwrap.machine as pnml


class RpcApiTest(ApiTest):
    """ Test ops for eventstore config and management """

    cli = ApiTest.client('api')
    oid = 'trial-' + time.time().__str__()
    schema = 'octoe'

    def setUp(self):
        """ """
        ApiTest.setUp(self)
        self.pool = psql.connect(**self.options)

        d = psql.drop_schema(self.schema, conn=self.pool)
        d.addCallback(lambda _: psql.create_schema(pnml.Machine(self.schema), conn=self.pool))
        return d

    def test_eventstore_db_schemata_admin(self):
        """ test write operation using a sequence of tic-tac-toe events """

        def create_stream(stream_already_exists):
            self.assertFalse(stream_already_exists)
            return self.cli.stream_create(self.schema, self.oid)

        def schema_exists(*_):
            return self.cli.schema_exists(self.schema)

        def stream_exists(schema_exists):
            return self.cli.stream_exists(self.schema, self.oid)

        def schema_destroy(_):
            self.assertTrue(schema_exists)
            return self.cli.schema_destroy(self.schema)

        def assert_destroyed(schema_exists):
            self.assertFalse(schema_exists)

        def schema_create(_):
            return self.cli.schema_create(self.schema, self.schema)

        def assert_created(schema_exists):
            self.assertTrue(schema_exists)
            return schema_exists

        d = schema_exists()
        d.addCallback(assert_created)
        d.addCallback(stream_exists)
        d.addCallback(schema_destroy)
        d.addCallback(assert_destroyed)
        d.addCallback(schema_create)
        d.addCallback(assert_created)

        return d
