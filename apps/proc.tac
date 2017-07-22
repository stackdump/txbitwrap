#!/usr/bin/env python
from txbitwrap.event import rdq, redispatch

SCHEMA='proc'

# TODO: convert this into ageneric task worker
# using the proc schema

def run(jobid, payload, **kwargs):
    """ before redispatch create a proc event stream """

    es = txbitwrap.storage(SCHEMA, **kwargs)
    es.storage.db.create_stream(jobid)
    event = es(oid=jobid, action='BEGIN', payload=json.dumps(payload))
    event['payload'] = payload
    event['schema'] = SCHEMA
    event['action'] = 'BEGIN'

    if 'id' not in event:
        raise Exception('failed to persist proc.state')

    if kwargs.get('reschedule', False):
        return redispatch(event)

    return rdq.put(event)