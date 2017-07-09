from twisted.internet import defer
from txbitwrap.event import bind, rdq
from txbitwrap.test import ApiTest

class EventHandlerTest(ApiTest):
    """ Test Event Handler """

    def test_event_put(self):
        d = defer.Deferred()

        event = {
            "schema": "octoe",
            "data": {
                "seq": 1,
                "timestamp": "2017-07-09T20:00:22.923493",
                "oid": "test",
                "id": "eaf2d67b052a5b641d4cbf0b19a0a7d0",
                "action": "BEGIN",
                "payload": {}
            }
        }

        def handler(options, event):
            d.callback((options, event))

        bind('octoe', {'test': 'data'}, handler)

        def test_event_handler(args):
            self.assertEquals(args[1]['schema'], 'octoe')
            self.assertEquals(args[0]['test'], 'data')

        job = rdq.put(event)

        d.addCallback(test_event_handler)

        return d
