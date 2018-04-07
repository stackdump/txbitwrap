""" defines web routes for bitwrap application """

import os
import json
import time
import cyclone.web
from cyclone.web import RequestHandler, StaticFileHandler
from twisted.internet import defer
import txbitwrap
from txbitwrap.api import headers, rpc
from txbitwrap.event import redispatch
from txbitwrap.event.broker import WebSocketBroker
import txbitwrap.machine as pnml

VERSION = '20180407'

def settings(options):
    """ append settings to api args """

    #options['cookie_secret'] = os.environ.get('COOKIE_SECRET', ''),
    #options['github_client_id']=os.environ.get('GITHUB_CLIENT_ID'),
    #options['github_secret']=os.environ.get('GITHUB_SECRET'),
    #login_url="/auth/login",
    #xsrf_cookies=True, # REVIEW: is this usable w/ rpc ?

    options['template_path'] = options.pop('template-path')
    options['debug'] = True

    return dict(options.items())

class Dispatch(headers.PostMixin, RequestHandler):
    """ /dispatch/{schema}/{oid} """

    @defer.inlineCallbacks
    def post(self, schema, oid, action, **kwargs):
        """ accepts a json post body as event payload """

        res = yield txbitwrap.eventstore(schema, **self.settings)(oid=oid, action=action, payload=self.request.body)
        self.write(res)
        res['payload'] = json.loads(self.request.body)
        res['schema'] = schema
        res['action'] = action

        redispatch(res)

class Broadcast(headers.PostMixin, RequestHandler):
    """ /broadcast/{schema}/{key} """

    def post(self, schema, key, **kwargs):
        """
        forward payload to message broker
        """

        handle = txbitwrap.eventstore(schema, **self.settings)
        res = { 'schema': schema, 'key': key, 'seq': time.time() }

        if self.request.body.startswith('{'):
            res['payload'] = json.loads(self.request.body)
            redispatch(res)
        else:
            res['__err__'] = 'no json found in body'

        self.write(res)

class Event(headers.Mixin, RequestHandler):
    """ /event/{schema}/{eventid} """

    @defer.inlineCallbacks
    def get(self, schema, key, *args):
        """ get event by eventid """
        handle = txbitwrap.eventstore(schema, **self.settings)
        res = yield handle.storage.db.events.fetch(key)
        self.write(res)

class State(headers.Mixin, RequestHandler):
    """ /state/{schema}/{oid} """

    @defer.inlineCallbacks
    def get(self, schema, key, *args):
        """ get head event by oid """

        handle = txbitwrap.eventstore(schema, **self.settings)
        res = yield handle.storage.db.states.fetch(key)
        self.write(res)

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
        self.write({'schemata': pnml.schema_list()})

class Stream(headers.Mixin, RequestHandler):
    """ /stream/{schema}/{oid} """

    
    @defer.inlineCallbacks
    def get(self, schema, key, *args):
        """ return event stream json array """
        try:
            stor = txbitwrap.eventstore(schema, **self.settings)
            stream = yield stor.storage.db.events.fetchall(key)
            self.write(json.dumps(stream))
        except Exception as x:
            # REVIEW: should this set 404 status
            self.write('[]')


class Config(headers.Mixin, RequestHandler):
    """ config """

    def get(self, stage, *args):
        """ direct web app to api """

        self.write({
            'endpoint': os.environ.get('ENDPOINT', 'http://' + self.request.host),
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
        (r"/", Index),
        (r"/(.*\.py)", StaticFileHandler, {"path": options['brython-path']})
    ]

    return cyclone.web.Application(handlers, **settings(options))
