"""
txbitwrap

usage:

    import txbitwrap
    m = txbitwrap.open('counter')
    m(oid='foo', action='INC', payload={}) # dispatch an event

"""
import os
from twisted.python import usage
from bitwrap_machine import ptnet
import bitwrap_psql as psql
from txbitwrap.event import rdq, bind, unbind
from txbitwrap.event.dispatch import Dispatcher

_STORE = {}

def factory(name, options):
    """ create twisted application """

    from twisted.application import service 

    app = service.Application(name)
    svc = service.MultiService()
    svc.addService(Dispatcher(rdq, options))
    svc.setServiceParent(app)

    return app

def storage(schema, **kwargs):
    """ open an evenstore by providing a schema name """

    if not schema in _STORE:
        _STORE[schema] = EventStore(schema, **kwargs)

    return _STORE[schema]

class EventStore(object):
    """ txbitwrap.EventStore """

    def __init__(self, schema, **kwargs):
        self.schema = schema.__str__()
        self.storage = psql.Storage(self.schema, **kwargs)

    def __call__(self, **request):
        """ execute a transformation """
        return self.storage.commit(request)

class Options(usage.Options):

    optParameters = (
        ("machine-path", "m", ptnet.PNML_PATH, "Path to read <schema>.xml"),
        ("listen-ip", "i", "0.0.0.0", "The listen address."),
        ("listen-port", "o", 8080, "The port number to listen on."),
        ("pg-host", "h", None, "psql host ; use env RDS_HOST=127.0.0.1"),
        ("pg-port", "r", 5432, "psql port"),
        ("pg-database", "d", None, "psql database name ; use env RDS_DB=<dbname>"),
        ("pg-username", "u", None, "psql username ; use env RDS_USER=<pg-user>"),
        ("pg-password", "p", None, "psql pass ; use env RDS_PASS=<pg-pass>"),
        ("rabbit-host", "q", None, "amqp username ; use env AMQP_USER=<rabbit>"),
        ("rabbit-port", "t", 5672, "amqp port"),
        ("rabbit-vhost", "v", None, "amqp vhost AMQP_VHOST=<vhost>"),
        ("rabbit-username", "n", None, "amqp username ; use env AMQP_USER=<rabbit>"),
        ("rabbit-password", "w", None, "amqp pass ; use env AMQP_PASS=<pass>"),
        ("api", "a", None, "run the cyclone web App ; use env var BITWRAP_API=1"),
        ("worker", "w", None, "handle events from API or Rabbit ; use env BITWRAP_WORKER=1"),
        ("external-queue", "x", None, "dispatch events using external message queue ; use env BITWRAP_QUEUE=bitwrap")
    )

    @staticmethod
    def append_env(options):
        def _opt(optkey, key, default):
            if options[optkey] is None:
                options[optkey] = os.environ.get(key, default)

        ptnet.set_pnml_path(options['machine-path'])

        _opt('pg-host', 'RDS_HOST', '127.0.0.1')
        _opt('pg-database', 'RDS_DB', 'bitwrap')
        _opt('pg-username', 'RDS_USER', 'postgres')
        _opt('pg-password', 'RDS_PASS', 'bitwrap')

        _opt('rabbit-host', 'AMQP_HOST', '127.0.0.1')
        _opt('rabbit-vhost', 'AMQP_VHOST', '/')
        _opt('rabbit-username', 'AMQP_USER', 'bitwrap')
        _opt('rabbit-password', 'AMQP_PASS', 'bitwrap')

        _opt('api', 'BITWRAP_API', None)
        _opt('worker', 'BITWRAP_WORKER', None)
        _opt('external-queue', 'BITWRAP_QUEUE', 'bitwrap')

        return options


    @staticmethod
    def from_env(overrides):
        options = Options()
        Options.append_env(options)

        for key, value in overrides.items():
            options[key] = value

        return options
