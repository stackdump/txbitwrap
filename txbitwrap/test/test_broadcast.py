""" Test EventStore """
import time
import json
from twisted.internet import defer
from txbitwrap.test import ApiTest
import txbitwrap.storage.postgres as pgsql
import txbitwrap.machine as pnml


class EventStoreTest(ApiTest):
    """ test bitwrap eventstore using tic-tac-toe """

    cli = ApiTest.client('api')

    def test_tic_tac_toe_sequence(self):
        """
        test write operation using a sequence of tic-tac-toe events
        """

        d = defer.Deferred()
        oid = 'trial-' + time.time().__str__()
        schema = 'octoe'
        pgsql.recreate_db(**self.options)
        pgsql.create_schema(pnml.Machine(schema), drop=True, **self.options)

        def assert_valid_body(res, code=200):
            """ test event response """
            self.assertEquals(res.code, code)
            obj = json.loads(res.body)
            print "\n", json.dumps(obj, indent=4)
            return obj

        def create_stream(exists):
            self.assertFalse(exists)
            return self.cli.stream_create(schema, oid)

        def create_trial_stream():
            """ add a new stream """

            def schema_exists(_):
                return self.cli.schema_exists(schema)

            def stream_exists(exists):
                self.assertTrue(exists)
                return self.cli.stream_exists(schema, oid)

            d.addCallback(schema_exists)
            d.addCallback(stream_exists)
            d.addCallback(create_stream)

        def dispatch_sequence(seq):
            """ add event sequence tests """

            def add_action(action):
                """ send an action event """

                def dispatch_event(_):
                    print "\n* tx-response\n"

                    return self.dispatch(
                        schema=schema,
                        oid=oid,
                        action=action,
                        payload={'trial': ['event', 'data']}
                    )

                d.addCallback(dispatch_event)
                d.addCallback(assert_valid_body)
 
            for action in seq:
                add_action(action)

        def rebroadcast():

            @defer.inlineCallbacks
            def _send_post_broadcast(obj):
                obj['schema'] = schema
                obj['action'] = 'FAK2'
                obj['payload'] = {'foo': 'bar'}
                res = yield self.broadcast(**obj)
                event = json.loads(res.body)
                print "\n", json.dumps(event, indent=4)

            d.addCallback(_send_post_broadcast)

        def run_tests():
            """ kick off testing """
            seq = ['BEGIN']

            create_trial_stream()
            dispatch_sequence(seq)
            rebroadcast()

        d.callback(run_tests())

        return d
