"""
bitwrap_io.api - this module defines web routes for bitwrap application
"""

import os
import cyclone.web
from cyclone.web import RequestHandler
from bitwrap_io.api import config, headers, api, pnml, machine, event, dispatch, stream, state

VERSION = 'v4'

class Index(RequestHandler):
    """ index """

    def get(self):
        self.render("index.html")

class Version(headers.Mixin, RequestHandler):
    """ index """

    def get(self):
        """ report api version """
        self.write({__name__: VERSION})

def factory(options):
    """ cyclone app factory """

    handlers = [
        (r"/dispatch/(.*)/(.*)/(.*)", dispatch.Resource),
        (r"/event/(.*)/(.*)", event.Resource),
        (r"/state/(.*)/(.*)", state.Resource),
        (r"/machine/(.*)", machine.Resource),
        (r"/pnml", pnml.Resource),
        (r"/stream/(.*)/(.*)", stream.Resource),
        (r"/config/(.*).json", config.Resource),
        (r"/version", Version),
        (r"/api", api.Handler),
        (r"/", Index)
    ]

    return cyclone.web.Application(handlers, **config.settings(options))
