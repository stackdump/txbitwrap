"""
return statevectors
"""
from cyclone.web import RequestHandler
import bitwrap_io.storage
from bitwrap_io.api import headers
import bitwrap_io
import json

class Resource(headers.Mixin, RequestHandler):
    """ /state/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ get head event by oid"""

        bw = bitwrap_io.open(schema, **self.settings)
        cursor = bw.storage.db.cursor()

        # FIXME: convert to template - some table names and types hardcoded
        sql = """
        SELECT
          to_json((ev.hash, st.oid, ev.action, st.rev, st.state, ev.payload, modified, created)::octoe.current_state)
        FROM
          octoe.states st
        JOIN
          octoe.events ev on ev.oid = st.oid and ev.seq = st.rev
        WHERE
          st.oid = '%s'
        """ % key

        cursor.execute(sql)
        self.write(cursor.fetchone()[0])
