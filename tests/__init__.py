"""
Test Suite for ath_core
"""

import unittest
import os
import sys

from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

# Bootstrap the external libs
TEST_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIR, '../external')))  # dependencies
sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIR, '../auth_core')))  # core code to test
sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIR, '../')))  # project root to import tests
sys.path.insert(0, TEST_DIR)  # test support for auth_core_settings etc


class TestCaseBase(unittest.TestCase):
    """
    Base Unit Test Case
    """
    is_unit = True

    def setUp(self):
        # Create a consistency policy that will simulate the High Replication consistency model.
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)

        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        self.testbed.init_taskqueue_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()

    def tearDown(self):
        self.testbed.deactivate()
