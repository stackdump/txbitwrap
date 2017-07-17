import os
import json
from cyclone.websocket import WebSocketHandler
from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor, task
from twisted.internet.protocol import ClientCreator
from twisted.python import log
from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
from txamqp.content import Content
import txamqp.spec

def __dispatcher(handle):
    """ Dispatcher singleton """
    Dispatcher.instance = handle

class Dispatcher(object):
    """
    Dispatch state machine events to RabbitMQ
    """

    handle = defer.Deferred()
    instance = None
    listeners = []

    def __init__(self, settings):
        spec = txamqp.spec.load(os.path.abspath(__file__ + '/../../specs/amqp0-9-1.stripped.xml'))
        self.settings = settings
        delegate = TwistedDelegate()

        cli = ClientCreator(
                reactor,
                AMQClient,
                delegate=delegate,
                vhost=self.settings['rabbit-vhost'],
                spec=spec).connectTCP(
                        self.settings['rabbit-host'],
                        self.settings['rabbit-port'])

        cli.addCallback(self.onConnect)
        cli.addErrback(lambda err: log.err(err))
        Dispatcher.handle.callback(self)

    def addCallback(self, listener):
        Deferred.listener.append(listener)

    def send(self, event):
        msg = Content(json.dumps(event))
        print("Sending message: %s" % msg)
        self.chan.basic_publish(exchange="bitwrap", content=msg, routing_key=event['schema'])

    @inlineCallbacks
    def onConnect(self, conn):
        """ on rabbit connected """

        self.conn = conn
        consumer_id=__name__

        log.msg("Connected to broker.")
        yield self.conn.authenticate(self.settings['rabbit-username'], self.settings['rabbit-password'])

        log.msg("Authenticated. Ready to send messages")
        self.chan = yield self.conn.channel(1)
        yield self.chan.channel_open()
        yield self.chan.queue_declare(queue='bitwrap', durable=True, exclusive=False)
        yield self.chan.exchange_declare(exchange="bitwrap", type="topic", durable=False )
        yield self.chan.queue_bind(queue='bitwrap', exchange="bitwrap", routing_key="*")
        yield self.chan.basic_consume(queue='bitwrap', no_ack=True, consumer_tag=consumer_id)

        queue = yield self.conn.queue(consumer_id)

        while True:
            d = defer.Deferred()
            msg = yield queue.get()
            print 'Received: ' + msg.content.body + ' from channel #' + str(self.chan.id)

            for dispatch in Dispatcher.listeners:
                d.addCallback(dispatch)

            d.callback(json.loads(msg.content.body))

Dispatcher.handle.addCallback(__dispatcher)
