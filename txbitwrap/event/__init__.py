from twisted.internet import defer
from txrdq.rdq import ResizableDispatchQueue
import uuid

HANDLERS = {}

def __dispatcher(event):
    """ dispatch job from rdq to HANDLERS """

    deferjob = defer.Deferred()

    def enqueue(handle):
        if handle not in HANDLERS:
            print '__NOHANDLE__', handle
            return

        for subscriber, dispatch in HANDLERS[handle].items():
            deferjob.addCallback(dispatch)

    enqueue(event['schema'])
    enqueue(event['schema'] + '.' + event['oid'])

    deferjob.callback(event)
    return deferjob

rdq = ResizableDispatchQueue(__dispatcher, 5)

def bind(handle_id, options, handler):
    """
    bind handler function to event dispatcher

    handler_id can be:
      a schema name: 'proc' or or 
      a composite key schema.oid: 'proc.myjobuuid'
      a tuple: ('proc', 'myjobuuid')
    """

    if not isinstance(handle_id, basestring):
        handle = list(handle_id).join('.')
    else:
        handle = handle_id

    if handler not in HANDLERS:
        HANDLERS[handle] = {}

    if 'subscriber_id' not in options:
        options['subscriber_id'] = str(uuid.uuid4())

    HANDLERS[handle][options['subscriber_id']] = lambda event: handler(options, event)

    return options['subscriber_id']

def unbind(handle_id, subscriber):
    """
    remove subscriber from event handler if it is bound
    """

    if not isinstance(handle_id, basestring):
        handle = list(handle_id).join('.')
    else:
        handle = handle_id

    if handle in HANDLERS:
        HANDLERS[handle].pop(subscriber)
        return True

    return False
