""" defines web routes for bitwrap application """

import os
import json
import time
import cyclone.web
from cyclone.web import RequestHandler
import txbitwrap
from txbitwrap.api import headers, rpc
from txbitwrap.event import redispatch
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

        res = txbitwrap.storage(schema, **self.settings)(oid=oid, action=action, payload=self.request.body)
        self.write(res)
        res['payload'] = json.loads(self.request.body)
        res['schema'] = schema
        res['action'] = action
        redispatch(res)

class Broadcast(headers.PostMixin, RequestHandler):
    """ /broadcast/{schema}/{key} """

    def post(self, schema, key, **kwargs):
        """
        forward an existing event to message broker
        optionally override existing fields by passing json in post body
        """

        handle = txbitwrap.storage(schema, **self.settings)
        res = handle.storage.db.events.fetch(key)
        res['msg'] = time.time()

        if self.request.body.startswith('{'):
            data = json.loads(self.request.body)


            _schema = data.get('schema')
            if _schema and _schema != schema:
                res['forged'] = True
                res['schema'] = _schema
            else:
                res['schema'] = schema

            _action = data.get('action')
            if _action and _action != res['action']:
                res['forged'] = True
                res['action'] = _action

            _payload = data.get('payload')
            if _payload and _payload != res['payload']:
                res['forged'] = True
                res['payload'] = _payload

        redispatch(res)
        self.write(res)

class Event(headers.Mixin, RequestHandler):
    """ /event/{schema}/{eventid} """

    def get(self, schema, key, *args):
        """ get event by eventid """
        handle = txbitwrap.storage(schema, **self.settings)
        self.write(handle.storage.db.events.fetch(key))

class State(headers.Mixin, RequestHandler):
    """ /state/{schema}/{oid} """

    def get(self, schema, key, *args):
        """ get head event by oid """

        handle = txbitwrap.storage(schema, **self.settings)
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
        stor = txbitwrap.storage(schema, **self.settings)
        self.write(json.dumps(stor.storage.db.events.fetchall(key)))

class Config(headers.Mixin, RequestHandler):
    """ config """

    def get(self, stage, *args):
        """ direct web app to api """

        self.write({
            'endpoint': os.environ.get('ENDPOINT', 'http://' + self.request.host),
            'wrapserver': os.environ.get('WRAPSERVER', 'http://127.0.0.1:8000'),
            'encoding': 'json',
            'version': VERSION,
            'stage': stage,
            'use_websocket': True
        })

class Index(RequestHandler):
    """ index """

    def get(self):
        self.render(
            "index.html",
            app_root=os.environ.get('APP_ROOT', ''),
            bundle_root=os.environ.get('BUNDLE_ROOT', 'https://bitwrap.io/txbitwrap')
        )

def factory(options):
    """ cyclone app factory """

    handlers = [
        (r"/dispatch/(.*)/(.*)/(.*)", Dispatch),
        (r"/broadcast/(.*)/(.*)", Broadcast),
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
