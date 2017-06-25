"""
run tests against a webserver running in the same reactor

NOTE: this test uses port 8888 on localhost
"""

import json
import cyclone.httpclient
from twisted.application import internet
from twisted.trial.unittest import TestCase
from bitwrap_io.api import factory as Api
from bitwrap_io.machine import pnml


IFACE = '127.0.0.1'
PORT = 8888

options = {
    'listen-ip': IFACE,
    'listen-port': PORT,
    'machine-path': './bitwrap_io/schemata',
    'pg-host': '127.0.0.1',
    'pg-port': 5432,
    'pg-username': 'postgres',
    'pg-password': 'bitwrap', # FIXME use pass for travis.ci
    'pg-database': 'bitwrap'
}

class ApiTest(TestCase):
    """ setup rpc endpoint and invoke ping method """

    def setUp(self):
        """ start tcp endpoint """

        self.options = options
        #pylint: disable=no-member
        self.service = internet.TCPServer(PORT, Api(options), interface=options['listen-ip'])
        #pylint: enable=no-member
        self.service.startService()

    def tearDown(self):
        """ stop tcp endpoint """
        self.service.stopService()


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
            data = json.dumps(event)

        return cyclone.httpclient.fetch(url, postdata=data)
