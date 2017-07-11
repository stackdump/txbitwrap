from twisted.internet import defer
import txbitwrap
from txbitwrap.event import bind, unbind, rdq
from txbitwrap.event.processor import run, redispatch
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
            """ play a game of tic-tac-toe """

            gamestore = txbitwrap.open('game', **OPTIONS)
            gameid = event['payload']['gameid']
            db = gamestore.storage.db

            if not db.stream_exists(gameid):
                db.create_stream(gameid)
                gamestore.storage.commit({ 'oid': gameid, 'action': 'BEGIN', 'payload': '{}'})
            else:
                # KLUDGE: just complete the game on 2nd invocation
                gamestore.storage.commit({ 'oid': gameid, 'action': 'END_X', 'payload': '{}'})

            state = db.states.fetch(gameid)['state']

            if state['complete'] == 1:
                d.callback((options, event)) # complete the test
            else:
                redispatch(event)

        subscriber_id = bind('proc', {'config': 'data'}, game_handler)

        def test_event_handler(args):
            self.assertEquals(args[1]['schema'], 'proc')
            self.assertEquals(args[0]['config'], 'data')
            

        d.addCallback(test_event_handler)
        d.addCallback(lambda _: unbind('proc', subscriber_id))
        job = run('job_uuid', { 'gameid': 'game_uuid' }, **self.options)

        return d
