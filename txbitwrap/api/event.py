"""
return statevectors
"""
from cyclone.web import RequestHandler
from bitwrap_io.api import headers
import bitwrap_io

class Resource(headers.Mixin, RequestHandler):
    """ /event/{schema}/{eventid} """

    def get(self, schema, key, *args):
        """ get event by eventid """
        handle = bitwrap_io.open(schema, **self.settings)
        self.write(handle.storage.db.events.fetch(key))
