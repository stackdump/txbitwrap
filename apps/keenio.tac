#!/usr/bin/env python
"""
Forwards events to keen.io

Configure by setting env vars:

export KEEN_PROJECT_ID='aaaaaaaaaaaaaaaaaaaaaaaa'
export KEEN_WRITE_KEY='xxxxxxxx...xxxxxxxxxxxxxxx'
export KEEN_SCHEMA=<bind-to-bitwrap-schema>

"""
import os
import json
from txbitwrap.event import processor
from cyclone.httpclient import fetch
from twisted.internet.protocol import Factory
Factory.noisy = False

PROJECT = os.environ['KEEN_PROJECT_ID']
WRITE_KEY = os.environ['KEEN_WRITE_KEY']
_API_URL = 'http://api.keen.io/3.0/projects/%s/events/%s'

class KeenIO(processor.Factory):

    def on_load(self):
        """ listen to all bitwrap events """
        print "Forwarding events to keen.io for schema: " + self.schema

        self.config = {
            'exchange': 'bitwrap',
            'queue': 'keen-io',
            'routing-key': self.schema
        }

        self.stor = None # does not use eventstore

    def on_event(self, opts, event):
        """ forward event to keen.io """

        print event
        url = (_API_URL % ( PROJECT, event['schema'] )).encode('latin-1')
        data = json.dumps(event)

        return fetch(
            url,
            headers={
                'Authorization': [WRITE_KEY],
                'Content-Type': ['application/json']
            },
            postdata=data
        )

app = KeenIO()
app.schema = os.environ.get('KEEN_SCHEMA', 'octoe')
application = app()
