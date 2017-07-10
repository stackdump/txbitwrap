import json
import txbitwrap
from txbitwrap.event import rdq

SCHEMA='proc'

def redispatch(event):
    return rdq.put(event)

def run(jobid, payload, **kwargs):
    es = txbitwrap.open(SCHEMA, **kwargs)
    es.storage.db.create_stream(jobid)
    event = es(oid=jobid, action='BEGIN', payload=json.dumps(payload))
    event['payload'] = payload
    event['schema'] = SCHEMA

    if not 'id' in event:
        raise Exception('failed to add proc evvent')

    return redispatch(event)
