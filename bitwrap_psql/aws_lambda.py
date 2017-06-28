"""
Lambda handler for bitwrap gateway api.
This handler expects events from these routes:

POST /api - admin rpc api
GET  /pnml - list schema names
GET  /machine/{schema} - get machine json

POST /dispatch/{schema}/{oid} - dispatch new event
GET  /stream/{schema}/{oid} - get all events by oid
GET  /state/{schema}/{oid} - get current state by oid
GET  /event/{schema}/{eventid} - get event by eventid
"""
# FIXME refactor to match latest changes for psql

import json
import bitwrap_io
#from bitwrap_io.storage import factory as StorageFactory # FIXME

def success(body):
    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(body)
    } 


def transform(event):
    """ perform a state machine transformation """
    msg = json.loads(event['body'])
    _s = msg['params'][0]['schema']

    err = None
    m = bitwrap_io.open(_s) # FIXME: add settings as kwargs

    preview = msg['method'] != 'transform'
    res = m.session(msg['params'][0]).commit(dry_run=preview)

    if (not preview) and (not res['id']):
        err = -1

    res['schema'] = _s

    return success({
        "result": res,
        "error": err,
        "id": msg['id']
    })

def query(event):
    """ query the eventstore """

    _p = event['pathParameters']
    _s = _p['schema']

    m = bitwrap_io.open(_s) #FIXME: add settings as kwargs
    s = StorageFactory(backend='postgresql')(_s, m) # FIXME: use correct storage
    # TODO: should use the machine object to access storage

    with s.db.cursor() as txn:

        if 'headid' in _p:
            head = s.db.state.head(_p["headid"])
            return success(s.db.events.get(head))

        elif 'eventid' in _p:
            evt = s.db.events.get(_p["eventid"])
            return success(evt)
        
        elif 'streamid' in _p:
            return success(s.db.events.list(_p["streamid"]))

        else:
            return success(m.machine.net.data)

def handler(event, context):
    """ dispatch gateway api event """

    if event['path'] == "/machine":
        return success(bitwrap_io.MACHINES.keys())

    if event['path'] == '/api':
        return transform(event)

    return query(event)
