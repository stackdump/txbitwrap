"""
return statevectors
"""
from cyclone.web import RequestHandler
from txbitwrap.api import headers
import txbitwrap

class Resource(headers.Mixin, RequestHandler):
    """ /state/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ get head event by oid """

        handle = txbitwrap.open(schema, **self.settings)
        self.write(handle.storage.db.states.fetch(key))
