""" txbitwrap.api.schemata """

from cyclone.web import RequestHandler
from bitwrap_machine import ptnet
from txbitwrap.api import headers

class Resource(headers.Mixin, RequestHandler):
    """ list PNML """

    def get(self, *args):
        """ list schema files """
        self.write({'schemata': ptnet.schema_list()})
