import json
import txbitwrap
from txbitwrap.event import rdq

SCHEMA='proc'

def run(jobid, data, **kwargs):
    es = txbitwrap.open(SCHEMA, **kwargs)
    es.storage.db.create_stream(jobid)
    res = es(oid=jobid, action='BEGIN', payload=json.dumps(data))
    res['payload'] = data

    if not 'id' in res:
        raise Exception('failed to add proc evvent')

    return rdq.put({ 'schema': 'proc', 'data': res})
