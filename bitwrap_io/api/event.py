"""
return statevectors
"""
from cyclone.web import RequestHandler
from bitwrap_io.api import headers
import bitwrap_io
import json

class Resource(headers.Mixin, RequestHandler):
    """ /event/{schema}/{eventid} """

    def get(self, schema, key, *args):
        """ get event by eventid """
        bw = bitwrap_io.open(schema, **self.settings)
        self.write(bw.storage.db.events.fetch(key))
