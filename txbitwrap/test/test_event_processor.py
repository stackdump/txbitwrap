from twisted.internet import defer
from txbitwrap.event import bind, rdq
from txbitwrap.event.processor import run
from txbitwrap.test import ApiTest, OPTIONS
import bitwrap_psql.db as pg
import bitwrap_machine as pnml

class EventProcessorTest(ApiTest):
    """ Test Event Handler """

    def test_event_put(self):
        pg.recreate_db(**self.options)
        pg.create_schema(pnml.Machine('proc'), drop=True, **self.options)

        d = defer.Deferred()

        def handler(options, event):
            d.callback((options, event))

        bind('proc', {'config': 'data'}, handler)

        def test_event_handler(args):
            self.assertEquals(args[1]['schema'], 'proc')
            self.assertEquals(args[0]['config'], 'data')

        job = run('job_uuid', { 'job': 'date' }, **self.options)

        d.addCallback(test_event_handler)

        return d
