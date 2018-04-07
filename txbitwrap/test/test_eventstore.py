""" Test EventStore """
import time
import json
from twisted.internet import defer
from twisted.python import log
from txbitwrap.test import ApiTest
import txbitwrap.storage.postgres as psql
import txbitwrap.machine as pnml


class EventStoreTest(ApiTest):
    """ test bitwrap eventstore using tic-tac-toe """

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

    def test_tic_tac_toe_sequence(self):
        """
        test write operation using a sequence of tic-tac-toe events
        """

        self.assertTrue(self.pool)

        def assert_valid_body(res, code=200):
            """ test event response """
            self.assertEquals(res.code, code)
            obj = json.loads(res.body)
            print "\n", json.dumps(obj, indent=4)
            return obj

        def test_eventstream(count=0):
            """ add stream tests"""

            d = self.fetch('stream/octoe/'+ self.oid)

            d.addCallback(assert_valid_body)
            d.addCallback(lambda obj: self.assertEquals(len(obj), count))

            return d

        def test_state():
            """ add state tests"""
            def _get_state(_):
                print "\n* state - latest"
                return self.fetch('state/octoe/'+ self.oid)

            def test_head_event(obj):
                print "\n* event - %i" % obj['rev']
                return self.fetch('event/octoe/'+ obj['id'])

            d =_get_state
            d.addCallback(assert_valid_body)
            d.addCallback(test_head_event)
            d.addCallback(assert_valid_body)
            return d


        def create_trial_stream():
            """ add a new stream """

            def schema_exists(schema):
                return self.cli.schema_exists(schema)

            def stream_exists(exists):
                self.assertTrue(exists)
                return self.cli.stream_exists(self.schema, self.oid)

            def create_stream(exists):
                self.assertFalse(exists)
                return self.cli.stream_create(self.schema, self.oid)

            d = schema_exists(self.schema)
            d.addCallback(stream_exists)
            d.addCallback(create_stream)
            return d

        @defer.inlineCallbacks
        def dispatch_sequence(seq):
            """ add event sequence tests """
            
            def _command(action):
                """ send an action event """

                return self.dispatch(
                    schema=self.schema,
                    oid=self.oid,
                    action=action,
                    payload={'trial': ['event', 'data']}
                )

            for action in seq:
                yield _command(action)


        def run_tests(_):
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

            d = dispatch_sequence(seq)
            d.addCallback(lambda _: test_eventstream(count=7))

            def _err(failure):
                print '__FAIL__'
                print failure

            d.addErrback(_err)
            return d
            #test_state()

        d = create_trial_stream()
        d.addCallback(run_tests)

        return d

    #def test_machine_api(self):
    #    """
    #    test readonly operations
    #    """ 
    #    d = defer.Deferred()
    #    schema = 'octoe'

    #    def assert_status_code(res, code=200):
    #        """ test event response """
    #        self.assertEquals(res.code, code)
    #        obj = json.loads(res.body)
    #        print "\n", json.dumps(obj, indent=4)
    #        return obj

    #    d.addCallback(lambda _: self.fetch('config/default.json'))
    #    d.addCallback(assert_status_code)

    #    d.addCallback(lambda _: self.fetch('schemata'))
    #    d.addCallback(assert_status_code)

    #    d.addCallback(lambda _: self.fetch('machine/%s' % schema))
    #    d.addCallback(assert_status_code)

    #    d.callback(None)

    #    return d
