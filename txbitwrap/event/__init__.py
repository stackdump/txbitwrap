from txrdq.rdq import ResizableDispatchQueue

HANDLERS = {}

def __dispatcher(event):
    if not event['schema'] in HANDLERS:
       return

    for dispatch in HANDLERS[event['schema']]:
       dispatch(event)

rdq = ResizableDispatchQueue(__dispatcher, 5)

def bind(schema, options, handler):
    """ bind handler function to event dispatcher """

    if schema not in HANDLERS:
        HANDLERS[schema] = []

    HANDLERS[schema].append(lambda event: handler(options, event))
