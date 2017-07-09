"""
txbitwrap.api.config - font end stats and config
"""

import os
from cyclone.web import RequestHandler
from txbitwrap.api import headers

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


class Resource(headers.Mixin, RequestHandler):
    """ config """

    def get(self, stage, *args):
        """ direct web app to api """

        self.write({
            'endpoint': os.environ.get('ENDPOINT', 'http://127.0.0.1:8080'),
        })
