"""
read from the event stream
"""
import json
from cyclone.web import RequestHandler
from bitwrap_io.api import headers
import bitwrap_io

class Resource(headers.Mixin, RequestHandler):
    """ /stream/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ return event stream json array """
        bw = bitwrap_io.open(schema, **self.settings)
        self.write(json.dumps(bw.storage.db.events.fetchall(key)))
