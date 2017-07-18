from twisted.internet import defer
from txrdq.rdq import ResizableDispatchQueue
from twisted.internet import defer
from txbitwrap.event.dispatch import Dispatcher
import uuid

HANDLERS = {}

def __worker(event):
    """ handle event on local reactor """
    deferjob = defer.Deferred()

    def __run(deferjob, handle):
        """ add job to rdq """
        if handle not in HANDLERS:
            #print '__NOHANDLE__', handle
            return

        for _, dispatch in HANDLERS[handle].items():
            deferjob.addCallback(dispatch)

    __run(deferjob, event['schema'])
    __run(deferjob, event['schema'] + '.' + event['oid'])

    deferjob.callback(event)
    return event

rdq = ResizableDispatchQueue(__worker, 5)

def redispatch(event):
    """ send AMQP event """
    if '__err__' not in event:
        if Dispatcher.instance is not None:
            Dispatcher.instance.send(event)
        else:
            rdq.put(event)

    return event

def bind(handle_id, options, handler):
    """
    bind handler function to event dispatcher
    returns subscriber-id
    """

    if not isinstance(handle_id, basestring):
        handle = '.'.join(handle_id)
    else:
        handle = handle_id

    if handler not in HANDLERS:
        HANDLERS[handle] = {}

    if 'subscriber_id' not in options:
        options['subscriber_id'] = str(uuid.uuid4())

    def __handle(event):
        """ wrapper around registered handler """
        handler(options, event)
        return event

    HANDLERS[handle][options['subscriber_id']] = __handle

    return options['subscriber_id']

def unbind(handle_id, subscriber):
    """
    remove subscriber from event handler if it is bound
    returns True when found / False when missing
    """

    if not isinstance(handle_id, basestring):
        handle = '.'.join(handle_id)
    else:
        handle = handle_id

    if handle in HANDLERS:
        HANDLERS[handle].pop(subscriber)
        return True

    return False
