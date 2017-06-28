"""
return statevectors
"""
from cyclone.web import RequestHandler
from bitwrap_io.api import headers
import bitwrap_io

class Resource(headers.Mixin, RequestHandler):
    """ /state/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ get head event by oid """

        bw = bitwrap_io.open(schema, **self.settings)
        self.write(bw.storage.db.states.fetch(key))
