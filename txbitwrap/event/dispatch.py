import os
import json
from zope.interface import implements
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.application.service import IService
from twisted.python import log
from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
from txamqp.content import Content
import txamqp.spec

def __dispatcher(ready):
    """ Dispatcher singleton """
    log.msg('__AMQP_DISPATCH_STARTED___')
    Dispatcher.instance = ready
    return ready

class Dispatcher(object):
    """
    Dispatch state machine events to RabbitMQ
    """

    implements(IService)

    ready = defer.Deferred()
    instance = None

    def __init__(self, rdq, settings):
        self.rdq = rdq
        self.listeners = []
        self.settings = settings
        self.name = __name__

    def privilegedStartService(self):
        pass

    def startService(self):
        spec = txamqp.spec.load(os.path.abspath(__file__ + '/../../specs/amqp0-9-1.stripped.xml'))

        delegate = TwistedDelegate()

        factory = ClientCreator(
            reactor,
            AMQClient,
            delegate=delegate,
            vhost=self.settings['rabbit-vhost'],
            spec=spec
        )
        
        cli = factory.connectTCP(
            self.settings['rabbit-host'],
            self.settings['rabbit-port']
        )

        cli.addCallback(self.onConnect)
        cli.addErrback(lambda err: log.err(err))
        Dispatcher.ready.callback(self)

    def stopService(self):
        # TODO: stop listening to rabbit
        pass

    def addListener(self, callback):
        """ """
        Deferred.listener.append(callback)

    @staticmethod
    @defer.inlineCallbacks
    def send(event):
        """ push to rabbit """
        self = Dispatcher.instance
        msg = Content(json.dumps(event))
        #log.msg("Sending message: %s" % msg)
        yield self.chan.basic_publish(exchange=self.settings['exchange'], content=msg, routing_key=event['schema'])
        defer.returnValue(event)

    @defer.inlineCallbacks
    def onConnect(self, conn):
        """ on rabbit connected """

        self.conn = conn
        consumer_id=__name__

        #log.msg("Connected to broker.")
        yield self.conn.authenticate(self.settings['rabbit-username'], self.settings['rabbit-password'])

        #log.msg("Authenticated. Ready to send messages")
        self.chan = yield self.conn.channel(1)
        yield self.chan.channel_open()
        yield self.chan.exchange_declare(exchange=self.settings['exchange'], type="topic", durable=False )
        yield self.chan.queue_declare(queue=self.settings['queue'], durable=True, exclusive=False)
        yield self.chan.queue_bind(queue=self.settings['queue'], exchange=self.settings['exchange'], routing_key=self.settings['routing-key'])

        self.listeners.append(lambda event: self.rdq.put(event))

        yield self.chan.basic_consume(queue=self.settings['queue'], no_ack=True, consumer_tag=consumer_id)
        queue = yield self.conn.queue(consumer_id)

        # TODO: add a way to end this gracefully
        # need to terminate when reactor receives shutdown signal
        while True:
            msg = yield queue.get()
            #log.msg('Received: ' + msg.content.body + ' from channel #' + str(self.chan.id))

            d = defer.Deferred()
            for dispatch in self.listeners:
                d.addCallback(dispatch)

            d.callback(json.loads(msg.content.body))

Dispatcher.ready.addCallback(__dispatcher)
