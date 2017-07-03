""" txbitwrap.api.machine """

from cyclone.web import RequestHandler
from txbitwrap.api import headers
import bitwrap_machine as pnml

class Resource(headers.Mixin, RequestHandler):
    """ Return state machine json """

    def get(self, name, *args):
        """ return state machine definition as json """

        handle = pnml.Machine(name)

        self.write({
            'machine': {
                'name': name,
                'places': handle.net.places,
                'transitions': handle.net.transitions
            }
        })
