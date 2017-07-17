import os
import json
from cyclone.websocket import WebSocketHandler
from txbitwrap.event import bind, unbind
from twisted.python import log

class WebSocketBroker(WebSocketHandler):
    """ provide a way for clients to subscribe to an event stream """

    def forward(self, options, event):
        """ forward event to WS & broker """
        self.sendMessage(json.dumps(event))

    def messageReceived(self, message):
        """
        write event to websocket and forward to AMQP exchange
        """

        msg = json.loads(message)
        log.msg('__msg__', msg)

        if 'bind' in msg:
            self.handle = msg['bind']
            self.subscription = bind(self.handle, {}, self.forward)

        if 'unbind' in msg:
            unbind(self.handle, self.subscription)


    def connectionMade(self):
        """ new websocket connection """
        log.msg('__connect__')

    def connectionLost(self, reason):
        log.msg('__close__', reason)
