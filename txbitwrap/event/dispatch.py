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

def __dispatcher(handle):
    """ Dispatcher singleton """
    Dispatcher.instance = handle
    return handle

class Dispatcher(object):
    """
    Dispatch state machine events to RabbitMQ
    """

    implements(IService)

    handle = defer.Deferred()
    instance = None
    listeners = []

    def __init__(self, rdq, settings):
        self.rdq = rdq
        self.settings = settings
        self.name = __name__

    def privilegedStartService(self):
        pass

    def startService(self):

        spec = txamqp.spec.load(os.path.abspath(__file__ + '/../../specs/amqp0-9-1.stripped.xml'))

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

    def stopService(self):
        # TODO: stop listening to rabbit
        pass

    def addCallback(self, listener):
        Deferred.listener.append(listener)

    def send(self, event):
        msg = Content(json.dumps(event))
        #log.msg("Sending message: %s" % msg)
        self.chan.basic_publish(exchange="bitwrap", content=msg, routing_key=event['schema'])

    @defer.inlineCallbacks
    def onConnect(self, conn):
        """ on rabbit connected """

        self.conn = conn
        consumer_id=__name__
        self.queue_name = self.settings['external-queue']

        #log.msg("Connected to broker.")
        yield self.conn.authenticate(self.settings['rabbit-username'], self.settings['rabbit-password'])

        #log.msg("Authenticated. Ready to send messages")
        self.chan = yield self.conn.channel(1)
        yield self.chan.channel_open()
        yield self.chan.queue_declare(queue=self.queue_name, durable=True, exclusive=False)
        yield self.chan.exchange_declare(exchange="bitwrap", type="topic", durable=False )
        yield self.chan.queue_bind(queue=self.queue_name, exchange="bitwrap", routing_key="*")

        if self.settings['worker'] and int(self.settings.get('worker', 0)) == 1:

            Dispatcher.listeners.append(lambda event: self.rdq.put(event))

            yield self.chan.basic_consume(queue=self.queue_name, no_ack=True, consumer_tag=consumer_id)
            queue = yield self.conn.queue(consumer_id)

            while True:
                d = defer.Deferred()
                msg = yield queue.get()
                #log.msg('Received: ' + msg.content.body + ' from channel #' + str(self.chan.id))

                for dispatch in Dispatcher.listeners:
                    d.addCallback(dispatch)

                d.callback(json.loads(msg.content.body))

Dispatcher.handle.addCallback(__dispatcher)
