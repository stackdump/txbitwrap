""" defines web routes for bitwrap application """

import os
import ujson as json
import time
import cyclone.web
from cyclone.auth import GithubMixin
from cyclone.web import RequestHandler, StaticFileHandler
from twisted.internet import defer
from twisted.python import log
import txbitwrap
from txbitwrap.api import headers, rpc
from txbitwrap.event import redispatch
from txbitwrap.event.broker import WebSocketBroker
import txbitwrap.machine as pnml

VERSION = '20180407'

def settings(options):
    """ append settings to api args """

    #options['cookie_secret'] = os.environ.get('COOKIE_SECRET', '')
    #xsrf_cookies=True, # REVIEW: is this usable w/ rpc ?
    options['github_client_id'] = os.environ.get('GITHUB_CLIENT_ID')
    options['github_secret'] = os.environ.get('GITHUB_SECRET')
    options['base_url'] = os.environ.get('BASE_URL', 'http://127.0.0.1:8080')
    options['login_uri'] = "/login"
    options['template_path'] = options.pop('template-path', None)
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

class GithubHandler(cyclone.web.RequestHandler, cyclone.auth.GithubMixin):
    """ Authenticate with github """


    @cyclone.web.asynchronous
    def get(self):
        access_code = self.get_argument("code", None)
        if access_code:
            def _callback(user_profile):
                if not user_profile:
                    self.redirect('/?auth=0')
                    return

                # TODO: do something  with this data
                # should probably store in a cookie and/session
                log.msg(user_profile['login'], user_profile['id'])

                self.redirect('/?auth=1')

                #{u'public_repos': 15,
                # u'site_admin': False,
                # u'subscriptions_url': u'https://api.github.com/users/stackdump/subscriptions',
                # u'gravatar_id': u'',
                # u'hireable': None,
                # u'id': 243500,
                # u'followers_url': u'https://api.github.com/users/stackdump/followers',
                # u'following_url': u'https://api.github.com/users/stackdump/following{/other_user}',
                # u'blog': u'https://www.blahchain.com/',
                # u'followers': 26,
                # u'location': u'Austin, TX',
                # u'type': u'User',
                # u'email': None,
                # u'bio': u'fan of State Machines and Blockchains - building event-sourcing tools',
                # u'gists_url': u'https://api.github.com/users/stackdump/gists{/gist_id}',
                # u'company': u'@bitwrap ',
                # u'events_url': u'https://api.github.com/users/stackdump/events{/privacy}',
                # u'html_url': u'https://github.com/stackdump',
                # u'updated_at': u'2018-05-03T12:33:49Z',
                # u'received_events_url': u'https://api.github.com/users/stackdump/received_events',
                # u'starred_url': u'https://api.github.com/users/stackdump/starred{/owner}{/repo}',
                # u'public_gists': 23,
                # u'name': u'Matt York',
                # u'organizations_url': u'https://api.github.com/users/stackdump/orgs',
                # u'url': u'https://api.github.com/users/stackdump',
                # u'created_at': u'2010-04-14T03:43:19Z',
                # u'avatar_url': u'https://avatars2.githubusercontent.com/u/243500?v=4',
                # u'repos_url': u'https://api.github.com/users/stackdump/repos',
                # u'following': 46,
                # u'login': u'stackdump'}

            d = self.get_authenticated_user(code=access_code)
            d.addCallback(_callback)
            # TODO: get user info!!
            #self.get_authenticated_user(self.async_callback(self._on_auth))
        else:
            self.authorize_redirect()

    def _on_auth(self, user):
        if not user:
            raise cyclone.web.HTTPError(500, "Github auth failed")
        # Save the user with, e.g., set_secure_cookie()

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
        (r"/login", GithubHandler),
        (r"/", Index),
        (r"/(.*\.py)", StaticFileHandler, {"path": options['brython-path']})
    ]

    return cyclone.web.Application(handlers, **settings(options))
