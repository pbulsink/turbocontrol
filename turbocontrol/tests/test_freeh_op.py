#!/usr/bin/env python

import unittest
from turbocontrol.utilities.freeh_op import Freeh, proc_freeh, FreehError
from turbocontrol.utilities.turbogo_helpers import write_file
import os

class TestFreeh(unittest.TestCase):
    """Tests the Jobset Class"""
    def setUp(self):
        self.freeh = Freeh(modvals={'tstart':'200', 'tend':'250'})
        self.freehfile = """          ------------------
           your wishes are :
          ------------------

  pstart=  0.1000E+00  pend=  0.1000E+00  nump=   1

  tstart=   298.1      tend=   298.1      numt=   1
 
           zero point vibrational energy
           -----------------------------
           zpe=   481.3     kJ/mol
 
   T        p       ln(qtrans) ln(qrot) ln(qvib) chem.pot.   energy    entropy
  (K)      (MPa)                                 (kJ/mol)   (kJ/mol) (kJ/mol/K)
 
 298.15   0.1000000      19.81    15.66    15.89    353.99    530.06   0.59886
 
   T        P              Cv            Cp       enthalpy
  (K)     (MPa)        (kJ/mol-K)    (kJ/mol-K)   (kJ/mol)
 298.15   0.1000000     0.2849985     0.2933128    532.54
 
"""
        write_file('testfreeh', self.freehfile.split('\n'))

    def tearDown(self):
        os.remove('testfreeh')
        os.remove('freeh')

    def test_setup_freeh(self):
        """Test setting up freeh"""
        self.assertEqual(self.freeh.modvalstring, 'tstart=200 tend=250')

    def test_freeh_proc(self):
        """Test the freehfile processing"""
        resultparams = {'pstart': '0.1000E+00', 'pend': '0.1000E+00',
                        'nump': '1', 'tstart': '298.1', 'tend': '298.1',
                        'numt': '1'}
        resultdata =  {'zpe': '481.3', 't': ['298.15'], 'p': ['0.1000000'],
                       'qtrans': ['19.81'], 'qrot': ['15.66'], 'qvib': ['15.89'],
                       'pot': ['353.99'], 'eng': ['530.06'], 'entr': ['0.59886'],
                       'cv': ['0.2849985'], 'cp': ['0.2933128'], 'enth': ['532.54']}
        funcparams, funcdata = proc_freeh('testfreeh')
        self.assertEqual(funcparams, resultparams)
        self.assertEqual(funcdata, resultdata)

    def test_start_cosmo(self):
        """Test starting cosmo"""
        with self.assertRaises(FreehError) as cm:
            self.freeh.run_freeh()
        the_exception = cm.exception
        self.assertEqual(the_exception.value, "Error starting freeh: The command was not found or was not executable: freeh. Check the environment is set up")


if __name__ == '__main__':
    unittest.main(verbosity=2)
