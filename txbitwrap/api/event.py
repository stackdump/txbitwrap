"""
return statevectors
"""
from cyclone.web import RequestHandler
from txbitwrap.api import headers
import txbitwrap

class Resource(headers.Mixin, RequestHandler):
    """ /event/{schema}/{eventid} """

    def get(self, schema, key, *args):
        """ get event by eventid """
        handle = txbitwrap.open(schema, **self.settings)
        self.write(handle.storage.db.events.fetch(key))
