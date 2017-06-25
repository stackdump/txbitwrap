"""
return statevectors
"""
from cyclone.web import RequestHandler
import bitwrap_io.storage
from bitwrap_io.api import headers
import bitwrap_io
import json

class Resource(headers.PostMixin, RequestHandler):
    """ /dispatch/{schema}/{oid} """

    def post(self, schema, oid, action, **kwargs):
        """
        # accepts a json post body

        EX: '{"action": "BEGIN", "oid": "trial-1497880691.3", "payload": {}, "schema": "octoe"}'
        """

        res = bitwrap_io.open(schema, **self.settings)(oid=oid, action=action, payload=self.request.body)
        self.write(res)
