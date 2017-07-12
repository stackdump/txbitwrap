import json
import txbitwrap
from txbitwrap.event import rdq

SCHEMA='proc'

def redispatch(event, reschedule=False):
    """
    enqueue event for further processing
    TODO: add pause/reschedule feature
    """

    return rdq.put(event)

def run(jobid, payload, **kwargs):
    """ before redispatch create a proc event stream """

    es = txbitwrap.open(SCHEMA, **kwargs)
    es.storage.db.create_stream(jobid)
    event = es(oid=jobid, action='BEGIN', payload=json.dumps(payload))
    event['payload'] = payload
    event['schema'] = SCHEMA
    event['action'] = 'BEGIN'

    if 'id' not in event:
        raise Exception('failed to persist proc.state')

    return redispatch(event)
