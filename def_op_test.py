#!/usr/bin/env python

import unittest
import os
from os import path
from def_op import Define
from turbogo import Job


class TestDefine(unittest.TestCase):
    """Tests the Jobset Class"""
    def setUp(self):
        self.define = Define()
        self.job = Job(name='test', ri=True, marij=True, disp=True)

    def test_start_define(self):
        """Test starting define"""
        self.assertEqual(self.define.start_define(), None)

    def test_setup_define(self):
        """Test parsing the variables"""
        self.assertEqual(self.define.setup_define(self.job), None)

    def test_exit(self):
        """Test exit code"""
        self.assertEqual(self.define._end_define(), -99)

if __name__ == '__main__':
    unittest.main(verbosity=2)
