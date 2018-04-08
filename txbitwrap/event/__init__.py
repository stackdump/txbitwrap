from twisted.internet import defer
from txrdq.rdq import ResizableDispatchQueue
from twisted.internet import defer
from txbitwrap.event.dispatch import Dispatcher
import uuid

HANDLERS = {}

def dispatch(handle, event):
    """ handle event on local reactor """
    if handle in HANDLERS:
        for _, dispatch in HANDLERS[handle].items():
            try:
                print '__DISPATCH__'
                print _
                print event
                dispatch(event)
            except Exception as ex:
                print '__DISPATCH_FAIL__'
                print ex

def __worker(event):
    """
    process events from rxrdq
    invokes handlers for <schema> and <schema>.<oid>
    """
    dispatch(event['schema'], event)
    dispatch(event['schema'] + '.' + event['oid'], event)
    return event

rdq = ResizableDispatchQueue(__worker, 1)

@defer.inlineCallbacks
def redispatch(event):
    """ send AMQP event """
    if '__err__' not in event:
        if Dispatcher.instance is not None:
            # no message queue just handle locally
            yield Dispatcher.send(event)
        else:
            yield rdq.put(event)

    defer.returnValue(event)

def bind(handle_id, options, handler):
    """
    bind handler function to event dispatcher
    returns subscriber-id
    """

    if not isinstance(handle_id, basestring):
        handle = '.'.join(handle_id)
    else:
        handle = handle_id

    if handle not in HANDLERS:
        HANDLERS[handle] = {}

    if 'subscriber_id' not in options:
        options['subscriber_id'] = str(uuid.uuid4())

    def __handle(event):
        """ wrapper around registered handler """
        handler(options, event)
        return event

    HANDLERS[handle][options['subscriber_id']] = __handle

    print HANDLERS

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

    flag = False
    if handle in HANDLERS:
        HANDLERS[handle].pop(subscriber)
        flag = True

    if len(HANDLERS[handle]) == 0:
        HANDLERS.pop(handle)

    return flag
