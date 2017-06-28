"""
Test Db migrations
"""
import time
from twisted.trial.unittest import TestCase
import bitwrap_psql.db as pg
import bitwrap_machine as pnml
from bitwrap_io.test import options


class SchemaTest(TestCase):


    def test_migration(self):
        """ """
        pg.create_db(pnml.Machine('counter'), drop=True, **options)
        pg.create_db(pnml.Machine('vote'), drop=False, **options)
        pg.create_db(pnml.Machine('octoe'), drop=False, **options)
