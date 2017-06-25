from zope.interface import implements

import os
from twisted.application import service, internet
from twisted.application.service import IServiceMaker, MultiService
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.plugin import IPlugin
from bitwrap_io.api import factory as ApiFactory
from twisted.python import usage
Factory.noisy = False

class Options(usage.Options):

    optParameters = (
        ("listen-ip", "i", "127.0.0.1", "The listen address."),
        ("listen-port", "o", 8080, "The port number to listen on."),
        ("syntax", "s", "json", "read [xml|json] files"),
        ("machine-path", "m", './bitwrap_io/schemata', "Path to read <schema-name>.[xml|json]"),
        ("pg-host", "h", '127.0.0.1', "psql host"),
        ("pg-port", "p", 5432, "psql port"),
        ("pg-username", "u", None, "psql username"),
        ("pg-password", "w", None, "psql pass"),
        ("pg-database", "d", None, "psql database name")
    )


class ServiceFactory(object):
    implements(IServiceMaker, IPlugin)

    tapname = "bitwrap"
    description = "bitwrap eventstore"
    options = Options

    def makeService(self, options):
        service = MultiService()

        bitwrap_node = internet.TCPServer(
            int(options['listen-port']),
            ApiFactory(options),
            interface=options['listen-ip'])

        service.addService(bitwrap_node)

        return service

serviceMaker = ServiceFactory()
