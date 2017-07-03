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
Factory.noisy = False

class Options(usage.Options):

    optParameters = (
        ("listen-ip", "i", "127.0.0.1", "The listen address."),
        ("listen-port", "o", 8080, "The port number to listen on."),
        ("machine-path", "m", ptnet.PNML_PATH, "Path to read <schema-name>.[xml|json]"),
        ("pg-port", "p", 5432, "psql port"),
        ("pg-host", "h", None, "psql host or use env RDS_HOST=127.0.0.1"),
        ("pg-database", "d", None, "psql database name or use env RDS_DB=bitwrap"),
        ("pg-username", "u", None, "psql username or use env RDS_USER=postgres"),
        ("pg-password", "w", None, "psql pass or use env RDS_PASS=<mypass>")
    )


class ServiceFactory(object):
    implements(IServiceMaker, IPlugin)

    tapname = "bitwrap"
    description = "bitwrap eventstore"
    options = Options

    def makeService(self, options):
        service = MultiService()

        ptnet.set_pnml_path(options['machine-path'])

        if options['pg-host'] is None:
            options['pg-host'] = os.environ.get('RDS_HOST', '127.0.0.1')

        if options['pg-database'] is None:
            options['pg-database'] = os.environ.get('RDS_DB', 'bitwrap')

        if options['pg-username'] is None:
            options['pg-username'] = os.environ.get('RDS_USER', 'postgres')

        if options['pg-password'] is None:
            options['pg-password'] = os.environ.get('RDS_PASS', 'bitwrap')



        bitwrap_node = internet.TCPServer(
            int(options['listen-port']),
            ApiFactory(options),
            interface=options['listen-ip'])

        service.addService(bitwrap_node)

        return service

serviceMaker = ServiceFactory()
