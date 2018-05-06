# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
# Copyright 2018 Matthew York
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Implementations of Github authentication schemes.

Allows a Request Handler to issues Json web tokens
"""

from cyclone import escape
from cyclone import httpclient
from cyclone.util import bytes_type
from cyclone.util import unicode_type
from cyclone.httputil import url_concat
from twisted.python import log

import base64
import binascii
import hashlib
import hmac
import time
import urllib
import urlparse
import uuid
import jwt
import datetime
import ujson as json

DecodeError = jwt.exceptions.DecodeError
ExpiredError = jwt.exceptions.ExpiredSignatureError

EXPIRE = 3600
ISSUER = 'txbitwrap:auth'
SECRET = 'e7kptEk$4ZUZ'


class JwtAuth(object):
    """ Authenticate with JWT """
    # FIXME add this feature

class OAuth2Mixin(object):
    """Abstract implementation of OAuth v 2."""

    def authorize_redirect(self, redirect_uri=None, client_id=None, client_secret=None, extra_params=None):
        """Redirects the user to obtain OAuth authorization for this service.

        Some providers require that you register a Callback
        URL with your application. You should call this method to log the
        user in, and then call get_authenticated_user() in the handler
        you registered as your Callback URL to complete the authorization
        process.
        """
        args = {
          "redirect_uri": redirect_uri,
          "client_id": client_id
        }
        if extra_params:
            args.update(extra_params)
        self.redirect(url_concat(self._OAUTH_AUTHORIZE_URL, args))

    def _oauth_request_token_url(self, redirect_uri=None, client_id=None, client_secret=None, code=None, extra_params=None):
        url = self._OAUTH_ACCESS_TOKEN_URL
        args = dict(
            redirect_uri=redirect_uri,
            code=code,
            client_id=client_id,
            client_secret=client_secret,
        )
        if extra_params:
            args.update(extra_params)
        return url_concat(url, args)


class GithubMixin(OAuth2Mixin):
    """
    Github Open ID / OAuth authentication. 

    https://developer.github.com/apps/building-oauth-apps/authorization-options-for-oauth-apps/#web-application-flow
    """
    _OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    _USER_API_URL = "https://api.github.com/user"

    def authorize_redirect(self):
        return OAuth2Mixin.authorize_redirect(self, **self._oauth_request_args())

    def _get_username(self, **kwargs):
        if 'error' in kwargs:
            log.msg('_get_username FAIL')
            log.msg(kwargs)
            return None

        _auth = "token %s" % kwargs['access_token']
        d = httpclient.fetch(
           self._USER_API_URL,
           headers={
               "Authorization": [_auth],
               "User-Agent": ['txbitwrap'],
               "Accept": ["application/json"]
           }
        )

        def _unpack(response):
            try:
                return json.loads(response.body)
            except:
                return None

        d.addCallback(_unpack)
        return d

    def get_authenticated_user(self, code=None):
        """Fetches the authenticated user data upon redirect."""
        post_args = {
            'client_id': self.settings['github_client_id'],
            'client_secret': self.settings['github_secret'],
            'code': code
        }
        d = httpclient.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            postdata=urllib.urlencode(post_args),
            headers={"Accept": ["application/json"]}
        )

        def _unpack(response):
            kwargs = json.loads(response.body)
            return self._get_username(**kwargs)

        d.addCallback(_unpack)

        return d

    def _oauth_request_args(self):
        self.require_setting("github_client_id", "Github OAuth")
        self.require_setting("github_secret", "Github OAuth")
        self.require_setting("login_uri", "Github OAuth")
        self.require_setting("base_url", "Github OAuth")

        return dict(
            client_id=self.settings["github_client_id"],
            client_secret=self.settings["github_secret"],
            redirect_uri=self.settings['base_url'] + self.settings['login_uri']
        )


# FIXME refactor to read response from github
def _oauth_parse_response(body):
    p = escape.parse_qs(body, keep_blank_values=False)
    token = dict(key=p["oauth_token"][0], secret=p["oauth_token_secret"][0])

    # Add the extra parameters the Provider included to the token
    special = ("oauth_token", "oauth_token_secret")
    token.update((k, p[k][0]) for k in p if k not in special)
    return token
