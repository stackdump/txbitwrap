"""
return statevectors
"""
from cyclone.web import RequestHandler
from txbitwrap.api import headers
import txbitwrap

class Resource(headers.PostMixin, RequestHandler):
    """ /dispatch/{schema}/{oid} """

    def post(self, schema, oid, action, **kwargs):
        """
        # accepts a json post body

        EX: '{"action": "BEGIN", "oid": "trial-1497880691.3", "payload": {}, "schema": "octoe"}'
        """

        res = txbitwrap.open(schema, **self.settings)(oid=oid, action=action, payload=self.request.body)
        self.write(res)
