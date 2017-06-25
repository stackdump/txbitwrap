
"""
Test Db migrations
"""
import time
from twisted.trial.unittest import TestCase
import bitwrap_io.storage.db as pg
from bitwrap_io.machine import pnml
from bitwrap_io.test import options


class SchemaTest(TestCase):


    def test_migration(self):
        """ """
        pg.create_db(pnml.Machine('counter'), drop=True, **options)
        pg.create_db(pnml.Machine('vote'), drop=False, **options)
        pg.create_db(pnml.Machine('octoe'), drop=False, **options)
