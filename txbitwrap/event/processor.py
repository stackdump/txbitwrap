import json
from txbitwrap import Dispatcher, Options, factory, bind, eventstore
import txbitwrap.machine as pnml
import txbitwrap.storage.postgres as pgsql
from twisted.python import log

class EventStoreMethods(object):
    """
    frendly dsl methods for eventstore
    """

    def dispatch(self, oid=None, action=None, payload=None, schema=None):
        """ send an event to the same schema this handler instances is using """

        if payload is None:
            payload = {}

        if schema is None:
            schema = self.schema

        res = eventstore(schema, **self.options)(oid=oid, action=action, payload=json.dumps(payload))

        res['schema'] = schema
        res['action'] = action
        res['payload'] = payload

        return Dispatcher.send(res)

    def exists(self, *args):
        """ load a bitwrap machine as a database schema """
        stor = eventstore(args[0], **self.options)

        if args[1]:
            return stor.storage.db.stream_exists(args[1])

        return stor.storage.db.schema_exists()

    def load(self, machine, schema=None):
        """ load a bitwrap machine as a database schema """
        if schema is None:
            name = machine
        else:
            name = schema
        return pgsql.create_schema(pnml.Machine(machine), schema_name=name, **self.options)

    def create(self, schema, oid):
        """ create a new stream """
        stor = eventstore(schema, **self.options)
        return stor.storage.db.create_stream(oid)

    def stream(self, schema, oid):
        """ get all events from a stream """
        stor = eventstore(schema, **self.options)
        return stor.storage.db.events.fetchall(oid)

    def state(self, schema, oid):
        stor = eventstore(schema, **self.options)
        return stor.storage.db.states.fetch(oid)['state']


class Factory(EventStoreMethods):
    """ event processor twisted application factory """

    def __call__(self):
        """ build twisted application """
        self.on_load()

        if not hasattr(self, 'config'):
            self.config = {
                'exchange': 'bitwrap',
                'queue': self.schema,
                'routing-key': self.schema
            }

        self.options = Options.from_env(self.config)
        log.msg(__name__, self.config)

        bind(self.schema, self.options, self.on_event)

        return factory(self.schema, self.options)


    def on_event(self, options, event):
        """ overload to handle events """
        pass

    def on_load(self):
        """ overload to add config """
        pass
