"""
Test Db migrations
"""
import time
from twisted.trial.unittest import TestCase
import bitwrap_psql.db as pg
import bitwrap_machine as pnml


class SchemaTest(TestCase):
    """ deploy machine schemata to database """

    def setUp(self):

        self.options = {
            'pg-host': '127.0.0.1',
            'pg-port': 5432,
            'pg-username': 'postgres',
            'pg-password': 'bitwrap',
            'pg-database': 'bitwrap'
        }


    def test_migration(self):
        """ recreate the DB """

        pg.create_db(pnml.Machine('counter'), drop=True, **self.options)
        pg.create_db(pnml.Machine('vote'), drop=False, **self.options)
        pg.create_db(pnml.Machine('octoe'), drop=False, **self.options)
