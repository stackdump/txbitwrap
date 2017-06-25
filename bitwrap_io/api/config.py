"""
bitwrap_io.api.config - font end stats and config
"""

import os
from cyclone.web import RequestHandler
from bitwrap_io.api import headers

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

        out = {
            'endpoint': os.environ.get('ENDPOINT', 'http://127.0.0.1:8080'),
            'wrapserver': os.environ.get('WRAPSERVER', 'http://127.0.0.1:8001'),
            'stage': stage
        }

        # KLUDGE: append all settings if using development pg-password
        if 'pg-password' in self.settings and self.settings['pg-password'] == 'bitwrap':
            out['settings'] = self.settings

        self.write(out)
