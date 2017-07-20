import json
import txbitwrap
from txbitwrap import Dispatcher, Options, factory, bind, storage

class Factory(object):
    """
    Event Processor Factory
    """

    def __init__(self):
        """ set config defaults """

        if not hasattr(self, 'config'):

            self.config = {
                'exchange': 'bitwrap',
                'queue': self.name,
                'routing-key': self.name
            }

    def __call__(self):
        """ build twisted application """

        if hasattr(self, 'on_load'):
            self.on_load()

        self.options = Options.from_env(self.config)
        self.stor = storage(self.name, **self.options)
        bind(self.name, self.options, self.on_event)

        return factory(self.name, self.options)

    def state(self, oid):
        return self.stor.storage.db.states.fetch(oid)['state']

    def dispatch(self, oid, action, payload):
        """ append event to eventstore and dispatch to rabbit """

        res = self.stor(oid=oid, action=action, payload=json.dumps(payload))
        res['schema'] = self.name
        res['action'] = action
        res['payload'] = payload

        return Dispatcher.send(res)

    def on_event(self, options, event):
        """ overload to handle events """
        pass
