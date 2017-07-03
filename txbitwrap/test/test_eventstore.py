"""
Test EventStore
"""
import time
import json
from twisted.internet import defer
from bitwrap_io.test import ApiTest
import bitwrap_psql.db as pg
import bitwrap_machine as pnml


class EventStoreTest(ApiTest):
    """ test bitwrap eventstore using tic-tac-toe """

    cli = ApiTest.client('api')

    def test_machine_api(self):
        """
        test readonly operations
        """
        d = defer.Deferred()
        schema = 'octoe'

        def assert_status_code(res, code=200):
            """ test event response """
            self.assertEquals(res.code, code)
            obj = json.loads(res.body)
            print "\n", json.dumps(obj, indent=4)
            return obj

        d.addCallback(lambda _: self.fetch('version'))
        d.addCallback(assert_status_code)

        d.addCallback(lambda _: self.fetch('config/default.json'))
        d.addCallback(assert_status_code)

        d.addCallback(lambda _: self.fetch('schemata'))
        d.addCallback(assert_status_code)

        d.addCallback(lambda _: self.fetch('machine/%s' % schema))
        d.addCallback(assert_status_code)

        d.callback(None)

        return d

    def test_tic_tac_toe_sequence(self):
        """
        test write operation using a sequence of tic-tac-toe events
        """

        d = defer.Deferred()
        oid = 'trial-' + time.time().__str__()
        schema = 'octoe'
        machine = pnml.Machine(schema)
        pg.create_db(machine, drop=True, **self.options)

        def assert_valid_body(res, code=200):
            """ test event response """
            self.assertEquals(res.code, code)
            obj = json.loads(res.body)
            print "\n", json.dumps(obj, indent=4)
            return obj

        def test_eventstream(count=0):
            """ add stream tests"""

            def _test(_):
                print "\n* event-stream"
                return self.fetch('stream/octoe/'+ oid)

            d.addCallback(_test)
            d.addCallback(assert_valid_body)
            d.addCallback(lambda obj: self.assertEquals(len(obj), count))

        def test_state():
            """ add state tests"""
            def _get_state(_):
                print "\n* state - latest"
                return self.fetch('state/octoe/'+ oid)

            def test_head_event(obj):
                print "\n* event - %i" % obj['rev']
                return self.fetch('event/octoe/'+ obj['id'])

            d.addCallback(_get_state)
            d.addCallback(assert_valid_body)
            d.addCallback(test_head_event)
            d.addCallback(assert_valid_body)

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

        def run_tests():
            """ kick off testing """
            seq = ['BEGIN',
                   'X11',
                   'O11', #invalid
                   'BAD', #invalid
                   'O01',
                   'X00',
                   'O20',
                   'X22',
                   'END_O']

            create_trial_stream()
            dispatch_sequence(seq)
            test_eventstream(count=7)
            test_state()

        d.callback(run_tests())

        return d
