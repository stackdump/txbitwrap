"""
return statevectors
"""
from cyclone.web import RequestHandler
import bitwrap_io.storage
from bitwrap_io.api import headers
import bitwrap_io
import json

class Resource(headers.Mixin, RequestHandler):
    """ /event/{schema}/{eventid} """

    def get(self, schema, key, *args):
        """ get event by eventid """

        sql = """
        SELECT
            row_to_json((hash, oid, seq, payload, timestamp)::%s.event_payload)
        FROM
            %s.events
        WHERE
            hash = '%s'
        ORDER BY seq DESC
        """  % (schema, schema, key)

        bw = bitwrap_io.open(schema, **self.settings)
        cursor = bw.storage.db.cursor()
        cursor.execute(sql)
        self.write(cursor.fetchone()[0])
