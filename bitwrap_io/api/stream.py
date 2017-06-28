"""
return statevectors
"""
from cyclone.web import RequestHandler
from bitwrap_io.api import headers
import bitwrap_io
import json

class Resource(headers.Mixin, RequestHandler):
    """ /stream/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ return event stream """
        bw = bitwrap_io.open(schema, **self.settings)
        self.write(json.dumps(bw.storage.db.events.fetchall(key)))
