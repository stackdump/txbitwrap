from zope.interface import implements

import os
from twisted.application import service, internet
from twisted.application.service import IServiceMaker, MultiService
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.plugin import IPlugin
from twisted.python import usage
from txbitwrap.api import factory as ApiFactory
from bitwrap_machine import ptnet
from txbitwrap.event.dispatch import Dispatcher
Factory.noisy = False

class Options(usage.Options):

    optParameters = (
        ("machine-path", "m", ptnet.PNML_PATH, "Path to read <schema>.xml"),
        ("listen-ip", "i", "0.0.0.0", "The listen address."),
        ("listen-port", "o", 8080, "The port number to listen on."),
        ("pg-host", "h", None, "psql host or use env RDS_HOST=127.0.0.1"),
        ("pg-port", "r", 5432, "psql port"),
        ("pg-database", "d", None, "psql database name or use env RDS_DB=<dbname>"),
        ("pg-username", "u", None, "psql username or use env RDS_USER=<pg-user>"),
        ("pg-password", "p", None, "psql pass or use env RDS_PASS=<pg-pass>"),
        ("rabbit-host", "q", None, "amqp username or use env AMQP_USER=<rabbit>"),
        ("rabbit-port", "t", 5672, "amqp port"),
        ("rabbit-vhost", "v", None, "amqp vhost AMQP_VHOST=<vhost>"),
        ("rabbit-username", "n", None, "amqp username or use env AMQP_USER=<rabbit>"),
        ("rabbit-password", "w", None, "amqp pass or use env AMQP_PASS=<pass>")
    )

class ServiceFactory(object):
    implements(IServiceMaker, IPlugin)

    tapname = "bitwrap"
    description = "bitwrap eventstore"
    options = Options

    def makeService(self, options):
        service = MultiService()

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

        Dispatcher(options)

        bitwrap_node = internet.TCPServer(
            int(options['listen-port']),
            ApiFactory(options),
            interface=options['listen-ip'])

        service.addService(bitwrap_node)

        return service

serviceMaker = ServiceFactory()
