"""
read from the event stream
"""
import json
from cyclone.web import RequestHandler
from txbitwrap.api import headers
import txbitwrap

class Resource(headers.Mixin, RequestHandler):
    """ /stream/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ return event stream json array """
        bw = txbitwrap.open(schema, **self.settings)
        self.write(json.dumps(bw.storage.db.events.fetchall(key)))
