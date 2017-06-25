"""
bitwrap_io.machine

Storage and Machine modules are combined to provide a persistent state machine.
StateMachine Schemata are expressed in Petri-Net Markup Language (xml) or using Bitwrap's internal DSL (json).
"""
from bitwrap_io.storage import Storage
import pnml

class StateMachine(object):
    """
    State Machine object with persistent storage
    """

    def __init__(self, schema, **kwargs):
        self.schema = schema.__str__()
        machine = pnml.Machine(self.schema)
        self.storage = Storage(self.schema, machine, **kwargs)

    def __call__(self, **request):
        """ execute a transformation """
        return self.session(request).commit()

    def session(self, request):
        """ begin a transaction """
        request['schema'] = self.schema
        return Transaction(request, self.storage)

class Transaction(object):
    """ state machine transaction """

    def __init__(self, request, storage):
        self.storage = storage
        self.request = request
        self.response = None

    def commit(self, dry_run=False):
        """ transform and persist state to storage """

        self.response = self.storage.commit(self.request, dry_run=dry_run)
        return self.response
