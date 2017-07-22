import json
import txbitwrap
from txbitwrap import Dispatcher, Options, factory, bind, storage

class EventStoreMethods(object):
    """
    frendly dsl methods for eventstore
    """

    def dispatch(self, oid=None, action=None, payload=None, schema=None):
        """ send an event to the same schema this handler instances is using """

        if payload is None:
            payload = {}

        msg = json.dumps(payload)

        if schema is None:
            schema = self.name
            res = self.stor(oid=oid, action=action, payload=msg)
        else:
            # TODO: test writing to other schemata
            # will this send error also?
            res = txbitwrap.storage(schema, **self.options)(oid=oid, action=action, payload=msg)

        res['schema'] = schema
        res['action'] = action
        res['payload'] = payload

        return Dispatcher.send(res)

    def get(self, schema, eventid):
        """ get an event """

    def load(self, machine_name, schema_name):
        """ load a bitwrap machine as a database schema """

    def create(self, schema, oid):
        """ create a new stream """

    def stream(self):
        """ get all events from a stream """

    def state(self, oid):
        return self.stor.storage.db.states.fetch(oid)['state']


class Factory(EventStoreMethods):
    """ event processor twisted application factory """

    def __call__(self):
        """ build twisted application """
        self.on_load()

        if not hasattr(self, 'config'):
            self.config = {
                'exchange': 'bitwrap',
                'queue': self.name,
                'routing-key': self.name
            }

        self.options = Options.from_env(self.config)
        self.stor = storage(self.name, **self.options)
        bind(self.name, self.options, self.on_event)

        return factory(self.name, self.options)


    def on_event(self, options, event):
        """ overload to handle events """
        pass

    def on_load(self):
        """ overload to add config """
        pass
