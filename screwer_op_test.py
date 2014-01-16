#!/usr/bin/env python

import unittest
from screwer_op import Screwer

class TestScrewer(unittest.TestCase):
    """Tests the Jobset Class"""
    def setUp(self):
        self.screwer = Screwer('5')

    def test_setup_screwer(self):
        """Test setting up screwer"""
        self.assertEqual(self.screwer.mode, '5')

    def test_exit_screwer(self):
        """Test exit code"""
        self.assertEqual(self.screwer._end_screwer(), -99)

if __name__ == '__main__':
    unittest.main(verbosity=2)
