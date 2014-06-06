#!/usr/bin/env python

import unittest
import os
from os import path
from def_op import Define, DefineError
from turbogo import Job


class TestDefine(unittest.TestCase):
    """Tests the Jobset Class"""
    def setUp(self):
        self.define = Define()
        self.job = Job(name='test', ri=True, marij=True, disp=True)

    def test_start_define(self):
        """Test starting define"""
        with self.assertRaises(DefineError) as cm:
            self.define.start_define()
        the_exception = cm.exception
        self.assertEqual(the_exception.value, "Error starting Define The command was not found or was not executable: define. Check the environment is set up")

    def test_setup_define(self):
        """Test parsing the variables"""
        self.assertEqual(self.define.setup_define(self.job), None)

    def test_exit(self):
        """Test exit code"""
        self.assertEqual(self.define._end_define(), -99)

if __name__ == '__main__':
    unittest.main(verbosity=2)
