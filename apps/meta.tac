#!/usr/bin/env python
"""
Handle upload and install events from 'models' stream
"""
import os
import json
from txbitwrap.event import processor
from cyclone.httpclient import fetch
from twisted.internet.protocol import Factory
Factory.noisy = False

class Meta(processor.Factory):

    schema = 'models'
    config = {
        'exchange': 'bitwrap',
        'queue': 'meta',
        'routing-key': '*'
    }

    def on_event(self, opts, event):
        """ TODO: read event URL on 'UPLOAD' events """

        if event['schema'] != 'models':
            return

        if event['action'] == 'UPLOAD':
            print event

            # TODO: download target pnml or json
            # ? store on models eventstream ?

app = Meta()
application = app()
