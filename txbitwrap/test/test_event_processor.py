from twisted.internet import defer
import txbitwrap
from txbitwrap.event import bind, rdq
from txbitwrap.event.processor import run
from txbitwrap.test import ApiTest, OPTIONS
import bitwrap_psql.db as pg
import bitwrap_machine as pnml

class EventProcessorTest(ApiTest):
    """ Test Event Handler """

    def test_event_put(self):
        """
        add an event handler for tic-tac-toe
        and run a proc to execute a game
        """
        pg.recreate_db(**self.options)
        pg.create_schema(pnml.Machine('proc'), drop=True, **self.options)
        pg.create_schema(pnml.Machine('octoe'), schema_name='game', drop=True, **self.options)

        d = defer.Deferred()

        def game_handler(options, event):
            gamestore = txbitwrap.open('game', **OPTIONS)
            gameid = event['data']['payload']['gameid']
            db = gamestore.storage.db

            if not db.stream_exists(gameid):
                db.create_stream(gameid)

            state = db.states.fetch(gameid)['state']

            # redispatch if not complete
            if state['complete'] == 0:
                #d.callback((options, event)) # complete the test
                pass

            #import IPython ; IPython.embed()

            #print options, event
            d.callback((options, event))

        bind('proc', {'config': 'data'}, game_handler)

        def test_event_handler(args):
            self.assertEquals(args[1]['schema'], 'proc')
            self.assertEquals(args[0]['config'], 'data')

        job = run('job_uuid', { 'gameid': 'game_uuid' }, **self.options)

        d.addCallback(test_event_handler)

        return d
