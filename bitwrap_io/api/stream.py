"""
return statevectors
"""
from cyclone.web import RequestHandler
import bitwrap_io.storage
from bitwrap_io.api import headers
import bitwrap_io
import json

class Resource(headers.Mixin, RequestHandler):
    """ /stream/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ return event stream """
        bw = bitwrap_io.open(schema, **self.settings)
        sql = """
        SELECT
            row_to_json((hash, oid, seq, payload, timestamp)::%s.event_payload)
        FROM
            %s.events
        WHERE
            oid = '%s'
        ORDER BY seq DESC
        """  % (schema, schema, key)

        cursor = bw.storage.db.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        self.write(json.dumps([row[0] for row in rows]))
