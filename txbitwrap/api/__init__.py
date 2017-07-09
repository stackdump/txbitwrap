""" defines web routes for bitwrap application """

import os
import json
import cyclone.web
from cyclone.web import RequestHandler
import txbitwrap
from txbitwrap.api import headers, rpc
from cyclone.jsonrpc import JsonrpcRequestHandler
import bitwrap_machine as pnml
import bitwrap_psql.db as pg

VERSION = 'v1'

def settings(options):
    """ append settings to api args """

    #options['cookie_secret'] = os.environ.get('COOKIE_SECRET', ''),
    #options['github_client_id']=os.environ.get('GITHUB_CLIENT_ID'),
    #options['github_secret']=os.environ.get('GITHUB_SECRET'),
    #login_url="/auth/login",
    #xsrf_cookies=True, # REVIEW: is this usable w/ rpc ?
    options['template_path'] = os.path.abspath(os.path.dirname(__file__) + '/../templates')
    options['debug'] = True

    if 'pg-database' in options:
        options['backend'] = 'postgresql'

    return dict(options.items())

class Dispatch(headers.PostMixin, RequestHandler):
    """ /dispatch/{schema}/{oid} """

    def post(self, schema, oid, action, **kwargs):
        """
        # accepts a json post body

        EX: '{"action": "BEGIN", "oid": "trial-1497880691.3", "payload": {}, "schema": "octoe"}'
        """

        res = txbitwrap.open(schema, **self.settings)(oid=oid, action=action, payload=self.request.body)
        self.write(res)

class Event(headers.Mixin, RequestHandler):
    """ /event/{schema}/{eventid} """

    def get(self, schema, key, *args):
        """ get event by eventid """
        handle = txbitwrap.open(schema, **self.settings)
        self.write(handle.storage.db.events.fetch(key))

class State(headers.Mixin, RequestHandler):
    """ /state/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ get head event by oid """

        handle = txbitwrap.open(schema, **self.settings)
        self.write(handle.storage.db.states.fetch(key))

class Machine(headers.Mixin, RequestHandler):
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

class Schemata(headers.Mixin, RequestHandler):
    """ list PNML """

    def get(self, *args):
        """ list schema files """
        self.write({'schemata': pnml.ptnet.schema_list()})

class Stream(headers.Mixin, RequestHandler):
    """ /stream/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ return event stream json array """
        bw = txbitwrap.open(schema, **self.settings)
        self.write(json.dumps(bw.storage.db.events.fetchall(key)))

class Config(headers.Mixin, RequestHandler):
    """ config """

    def get(self, stage, *args):
        """ direct web app to api """

        self.write({
            'endpoint': os.environ.get('ENDPOINT', 'http://127.0.0.1:8080'),
        })

class Version(headers.Mixin, RequestHandler):
    """ index """

    def get(self):
        """ report api version """
        self.write({__name__: VERSION})

class Index(RequestHandler):
    """ index """

    def get(self):
        self.render("index.html")

def factory(options):
    """ cyclone app factory """

    handlers = [
        (r"/dispatch/(.*)/(.*)/(.*)", Dispatch),
        (r"/event/(.*)/(.*)", Event),
        (r"/state/(.*)/(.*)", State),
        (r"/machine/(.*)", Machine),
        (r"/schemata", Schemata),
        (r"/stream/(.*)/(.*)", Stream),
        (r"/config/(.*).json", Config),
        (r"/version", Version),
        (r"/api", rpc.Rpc),
        (r"/", Index)
    ]

    return cyclone.web.Application(handlers, **settings(options))
