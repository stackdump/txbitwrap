from cyclone.websocket import WebSocketHandler
from txbitwrap.event import bind, unbind
import json

class Broker(WebSocketHandler):
    """ provide a way for clients to subscribe to an event stream """

    def messageReceived(self, message):
        print '__msg__', message
        msg = json.loads(message)

        def forward(options, event):
            """ forward event to websocket """
            self.sendMessage(json.dumps(event))

        if 'bind' in msg:
            self.handle = msg['bind']
            self.subscription = bind(self.handle, {}, forward)

        if 'unbind' in msg:
            unbind(self.handle, self.subscription)


    def connectionMade(self):
        print '__connect__'

    def connectionLost(self, reason):
        try:
            unbind(self.handle, self.subscription)
        except:
            pass

        print '__close__', reason
