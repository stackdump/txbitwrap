from cyclone.web import RequestHandler, asynchronous
from cyclone.websocket import WebSocketHandler
from twisted.internet import task
from txbitwrap.api import headers
from twisted.web import server
from txbitwrap.event import bind, unbind
import time
import json

class Observe(WebSocketHandler):

    def messageReceived(self, message):
        print '__msg__', message
        msg = json.loads(message)

        def dispatch(options, event):
            self.sendMessage(json.dumps(event))

        if 'bind' in msg:
            self.handle = msg['bind']
            self.subscription = bind(self.handle, {}, dispatch)

        if 'unbind' in msg:
            unbind(self.handle, self.subscription)


    def connectionMade(self):
        print '__connect__'

    def connectionLost(self, reason):
        print '__close__', reason
