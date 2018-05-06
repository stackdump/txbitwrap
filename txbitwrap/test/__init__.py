"""
run tests against a webserver running in the same reactor

NOTE: this test uses port 8888 on localhost
"""

import os
import ujson as json
import cyclone.httpclient
from twisted.internet import defer
from twisted.application import internet
from twisted.trial.unittest import TestCase
from twisted.python import log
from txbitwrap.api import factory as Api
from txbitwrap.machine import set_pnml_path
import txbitwrap.event


IFACE = '127.0.0.1'
PORT = 8888

OPTIONS = {
    'listen-ip': IFACE,
    'listen-port': PORT,
    'machine-path': os.path.abspath(os.path.dirname(__file__) + '/../../schemata'),
    'pg-host': '127.0.0.1',
    'pg-port': 5432,
    'pg-username': 'bitwrap',
    'pg-password': 'bitwrap',
    'pg-database': 'bitwrap'
}

class ApiTest(TestCase):
    """ setup rpc endpoint and invoke ping method """

    def setUp(self):
        """ start tcp endpoint """

        set_pnml_path(OPTIONS['machine-path'])
        self.options = OPTIONS
        #pylint: disable=no-member
        self.service = internet.TCPServer(PORT, Api(self.options), interface=self.options['listen-ip'])
        #pylint: enable=no-member
        self.service.startService()

    @defer.inlineCallbacks
    def tearDown(self):
        """ stop tcp endpoint """
        self.service.stopService()
        yield txbitwrap.event.rdq.stop()

    @staticmethod
    def url(resource):
        """ bulid a url using test endpoint """
        return 'http://%s:%s/%s' % (IFACE, PORT, resource)

    @staticmethod
    def client(resource):
        """ rpc client """
        return cyclone.httpclient.JsonRPC(ApiTest.url(resource))

    @staticmethod
    def fetch(resource, **kwargs):
        """ async request with httpclient"""
        return cyclone.httpclient.fetch(ApiTest.url(resource), **kwargs)

    @staticmethod
    def dispatch(**event):
        """ rpc client """

        resource = 'dispatch/%s/%s/%s' % (event['schema'], event['oid'], event['action'])
        url = ApiTest.url(resource)

        if isinstance(event['payload'], str):
            data = event['payload']
        else:
            data = json.dumps(event['payload'])

        return cyclone.httpclient.fetch(url, postdata=data)

    @staticmethod
    def broadcast(**event):
        """ rpc client """

        resource = 'broadcast/%s/%s' % (event['schema'], event['id'])
        url = ApiTest.url(resource)
        data = json.dumps(event)

        return cyclone.httpclient.fetch(url, postdata=data)
