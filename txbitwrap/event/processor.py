import txbitwrap
from txbitwrap.event import rdq
import json

SCHEMA='proc'

def run(jobid, data, **kwargs):
    es = txbitwrap.open(SCHEMA, **kwargs)
    es.storage.db.create_stream(jobid)
    res = es(oid=jobid, action='BEGIN', payload=json.dumps(data))

    if not 'id' in res:
        raise Exception('failed to add proc evvent')

    return rdq.put({ 'schema': 'proc', 'data': res})
