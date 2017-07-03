""" bitwrap_io.api.schemata """

from cyclone.web import RequestHandler
from bitwrap_machine import ptnet
from bitwrap_io.api import headers

class Resource(headers.Mixin, RequestHandler):
    """ list PNML """

    def get(self, *args):
        """ list schema files """
        self.write({'schemata': ptnet.schema_list()})
