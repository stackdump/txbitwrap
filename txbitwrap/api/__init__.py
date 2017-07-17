""" defines web routes for bitwrap application """

import os
import json
import cyclone.web
from cyclone.web import RequestHandler
import txbitwrap
from txbitwrap.api import headers, rpc
from txbitwrap.event.processor import redispatch
from txbitwrap.event.broker import WebSocketBroker
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

    return dict(options.items())

class Dispatch(headers.PostMixin, RequestHandler):
    """ /dispatch/{schema}/{oid} """

    def post(self, schema, oid, action, **kwargs):
        """ accepts a json post body as event payload """

        res = txbitwrap.open(schema, **self.settings)(oid=oid, action=action, payload=self.request.body)
        self.write(res)
        res['payload'] = json.loads(self.request.body)
        res['schema'] = schema
        res['action'] = action
        redispatch(res)

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
        estor = txbitwrap.open(schema, **self.settings)
        self.write(json.dumps(estor.storage.db.events.fetchall(key)))

class Config(headers.Mixin, RequestHandler):
    """ config """

    def get(self, stage, *args):
        """ direct web app to api """

        self.write({
            'endpoint': os.environ.get('ENDPOINT', 'http://127.0.0.1:8080'),
            'encoding': 'json',
            'version': VERSION,
            'stage': stage
        })

class Index(RequestHandler):
    """ index """

    def get(self):
        self.render("index.html")

def factory(options):
    """ cyclone app factory """

    handlers = [
        (r"/dispatch/(.*)/(.*)/(.*)", Dispatch),
        (r"/websocket", WebSocketBroker),
        (r"/event/(.*)/(.*)", Event),
        (r"/state/(.*)/(.*)", State),
        (r"/machine/(.*)", Machine),
        (r"/schemata", Schemata),
        (r"/stream/(.*)/(.*)", Stream),
        (r"/config/(.*).json", Config),
        (r"/api", rpc.Rpc),
        (r"/", Index)
    ]

    return cyclone.web.Application(handlers, **settings(options))
