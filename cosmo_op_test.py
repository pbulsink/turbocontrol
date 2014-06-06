#!/usr/bin/env python

import unittest
from cosmo_op import Cosmo, CosmoError
from turbogo import Job

class TestCosmo(unittest.TestCase):
    """Tests the Jobset Class"""
    def setUp(self):
        self.cosmo = Cosmo()
        job = Job(cosmo='38')
        self.cosmo.setup_cosmo(job)

    def test_setup_cosmo(self):
        """Test setting up cosmo"""
        self.assertEqual(self.cosmo.epsilon, '38')

    def test_start_cosmo(self):
        """Test starting cosmo"""
        with self.assertRaises(CosmoError) as cm:
            self.cosmo.start_cosmo()
        the_exception = cm.exception
        self.assertEqual(the_exception.value, "Error starting cosmoprep: The command was not found or was not executable: cosmoprep. Check the environment is set up")

if __name__ == '__main__':
    unittest.main(verbosity=2)
