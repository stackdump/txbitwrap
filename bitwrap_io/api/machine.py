""" bitwrap_io.api.machine """

from cyclone.web import RequestHandler
import bitwrap_io
from bitwrap_io.api import headers
import bitwrap_machine as pnml

class Resource(headers.Mixin, RequestHandler):
    """ Return state machine json """

    def get(self, name, *args):
        """ return state machine definition as json """

        sm = pnml.Machine(name)

        self.write({
            'machine': {
                'name': name,
                'places': sm.net.places,
                'transitions': sm.net.transitions
            }
        })
