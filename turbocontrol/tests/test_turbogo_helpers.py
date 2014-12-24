#!/usr/bin/env python
"""Helper Testsuite"""

import unittest
import os
from turbocontrol.utilities.turbogo_helpers import *
from turbocontrol.turbogo import Job

class TestSimpleFuncs(unittest.TestCase):
    """Test the simple functions"""

    def setUp(self):
        write_file('testfile1', ['testfile1',''])
        write_file('testfile2', ['testfile2',''])

    def tearDown(self):
        os.remove('testfile1')
        os.remove('testfile2')

    def test_is_int_int(self):
        """Test the is_int function with a good int"""
        self.assertEqual(is_int(1), True)

    def test_is_int_string(self):
        """Test the is_int function with a good str"""
        self.assertEqual(is_int('1'), True)

    def test_is_int_negative(self):
        """Test the is_int function with a good negative string"""
        self.assertEqual(is_int('-1'), True)

    def test_is_int_float(self):
        """Test the is_int function with a bad float"""
        self.assertEqual(is_int('1.01'), False)

    def test_is_int_fail(self):
        """Test the is_int function with a bad string"""
        self.assertEqual(is_int('one'), False)

    def test_is_positive_int_pgood(self):
        """Test the is_positive_int function with a good value"""
        self.assertEqual(is_positive_int(1), True)

    def test_is_positive_int_ngood(self):
        """Test the is_positive_int function with a bad value"""
        self.assertEqual(is_positive_int(-1), False)

    def test_is_positive_int_string(self):
        """Test the is_positive_int function with a good string"""
        self.assertEqual(is_positive_int('1'), True)

    def test_is_positive_int_negative(self):
        """Test the is_positive_int function with a bad string"""
        self.assertEqual(is_positive_int('-1'), False)

    def test_is_positive_int_fail(self):
        """Test the is_positive_int function with a bad word"""
        self.assertEqual(is_positive_int('one'), False)

    def test_is_float_pgood(self):
        """Test the is_float function with a good value"""
        self.assertEqual(is_float(1.01), True)

    def test_is_float_ngood(self):
        """Test the is_float function with a good negative"""
        self.assertEqual(is_float(-1.01), True)

    def test_is_float_string(self):
        """Test the is_float function with a good string"""
        self.assertEqual(is_float('1.01'), True)

    def test_is_float_negative(self):
        """Test the is_float function with a good negative string"""
        self.assertEqual(is_float('-1.01'), True)

    def test_is_float_int(self):
        """Test the is_float function with a good int"""
        self.assertEqual(is_float(1), True)

    def test_is_float_strint(self):
        """Test the is_float function with a good int string"""
        self.assertEqual(is_float('1'), True)

    def test_is_float_fail(self):
        """Test the is_float function with a bad string"""
        self.assertEqual(is_float('one'), False)

    def test_slug_numeric_one(self):
        """Test the slug function with a number"""
        self.assertEqual(slug('1'), '1')

    def test_slug_numeric_many(self):
        """Test the slug function with a few numbers"""
        self.assertEqual(slug('1 2 3 '), '1-2-3')

    def test_slug_alphanumeric_one(self):
        """Test the slug function with a word"""
        self.assertEqual(slug('Hello'), 'hello')

    def test_slug_alphanumeric_many(self):
        """Test the slug function with alphanumeric words"""
        self.assertEqual(slug('Today is 3 degrees'), 'today-is-3-degrees')

    def test_slug_special(self):
        """Test the slug function with a character"""
        self.assertEqual(slug('My Phone # is 555-1234.'),
                         'my-phone-is-555-1234')

    def test_file_exists_true(self):
        """Test the file_exists function with a list"""
        self.assertEqual(check_files_exist(['testfile1', 'testfile2']), True)

    def test_file_exists_false(self):
        """Test the file_exists function with a file not exists"""
        self.assertEqual(check_files_exist(['testfile3']), False)

    def test_list_str(self):
        """Test the list_str function with a list"""
        self.assertEqual(list_str(['a', 'b', 'c']), 'a\nb\nc')

    def test_time_readable_zero(self):
        """Test the time_readable function with 0"""
        self.assertEqual(time_readable(0), '0:00:00')

    def test_time_readable_neg(self):
        """Test the time_readable function with negative value"""
        self.assertEqual(time_readable(-600), '0')

    def test_time_readable_harder(self):
        """Test the time_readable function with a harder time"""
        self.assertEqual(time_readable(5000), '1:23:20')

    def test_check_env(self):
        """Test checking the local env. May fail depending on where this is run"""
        self.assertEqual(check_env(), {'TURBODIR':'/share/apps/turbomole/6.5',
                                       'TURBOMOLE_SYSNAME': 'em64t-unknown-linux-gnu'})
    


class TestArgs(unittest.TestCase):
    """Test the args testers"""

    def setUp(self):
        self.nprocarg = ['%nproc=8']
        self.archarg = ['%arch=GA']
        self.maxcyclesarg = ['%maxcycles=300']
        self.autocontrolmodarg = ['%autocontrolmod']
        self.nocontrolmodarg = ['%nocontrolmod']
        self.bad_nprocarg = ['%nproc=10']
        self.bad_archarg = ['%arch=GAP']
        self.bad_maxcyclesarg = ['%maxcycles=-5']
        self.good_cosmo = ['%cosmo=DMF']
        self.good_lower_cosmo = ['%cosmo=dmf']
        self.bad_cosmo = ['%cosmo=blarg']
        self.none_cosmo = ['%cosmo']
        self.number_cosmo = ['%cosmo=38.4']
        self.bad_rt = ['%rt=numbers']
        self.good_rt = ['%rt=10']
        self.bad_controlmodarg = ['%autocontrolmod', '%nocontrolmod']
        self.unknownarg = ['%billy']
        self.ignorearg = ['%rwf=billy.rwf']
        self.multiarg = ['%nproc=8', '%arch=GA', '%maxcycles=300', '%nosave']

    def test_nprocarg(self):
        """Test the collection of nprocs"""
        self.assertEqual(check_args(self.nprocarg), {'nproc': '8'})

    def test_bad_nprocarg(self):
        """Test a bad nproc"""
        with self.assertRaises(InputCheckError) as cm:
            check_args(self.bad_nprocarg)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, "Invalid value 10 for argument nproc.")

    def test_archarg(self):
        """Test getting an architecture"""
        self.assertEqual(check_args(self.archarg), {'arch': 'GA'})

    def test_bad_archarg(self):
        """Test a bad architecture"""
        with self.assertRaises(InputCheckError) as cm:
            check_args(self.bad_archarg)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, "Invalid value GAP for argument arch.")

    def test_maxcyclesarg(self):
        """Test the max cycle"""
        self.assertEqual(check_args(self.maxcyclesarg), {'iterations': '300'})

    def test_bad_maxcyclesarg(self):
        """Test bad maxcycles"""
        with self.assertRaises(InputCheckError) as cm:
            check_args(self.bad_maxcyclesarg)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, "Invalid value -5 for argument maxcycles.")

    def test_autocontrolmodarg(self):
        """Test applying autocontrolmod"""
        self.assertEqual(check_args(self.autocontrolmodarg), {'mod': True})

    def test_nocontrolmodarg(self):
        """Test turning off autocontrolmod"""
        self.assertEqual(check_args(self.nocontrolmodarg), {'mod': False})

    def test_bad_controlmodarg(self):
        """test both autocontrolmods together"""
        with self.assertRaises(InputCheckError) as cm:
            check_args(self.bad_controlmodarg)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, "More than one control modify flag passed.")

    def test_ignorearg(self):
        """Test an arg to ignore"""
        self.assertEqual(check_args(self.ignorearg), {})

    def test_bad_unknownarg(self):
        """Test an unknown arg"""
        with self.assertRaises(InputCheckError) as cm:
            check_args(self.unknownarg)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, "Invalid argument billy.")

    def test_multiarg(self):
        result = {'nproc': '8', 'arch': 'GA', 'iterations':'300'}
        self.assertEqual(check_args(self.multiarg), result)

    def test_good_upper_cosmo(self):
        """Test a good cosmo"""
        self.assertEqual(check_args(self.good_cosmo), {'cosmo': '38'})

    def test_good_lower_cosmo(self):
        """Test a good cosmo with lowercase letters"""
        self.assertEqual(check_args(self.good_lower_cosmo), {'cosmo': '38'})
    
    def test_bad_cosmo(self):
        """Test a bad cosmo"""
        self.assertEqual(check_args(self.bad_cosmo), {})
    
    def test_no_cosmo(self):
        """Test a blank cosmo"""
        self.assertEqual(check_args(self.none_cosmo), {'cosmo': ''})

    def test_number_cosmo(self):
        """Test an explicit number"""
        self.assertEqual(check_args(self.number_cosmo), {'cosmo': '38.4'})

    def test_rt(self):
        """Test an rt"""
        self.assertEqual(check_args(self.good_rt), {'rt': 10})

    def test_bad_rt(self):
        """Test a bad rt"""
        self.assertEqual(check_args(self.bad_rt), {'rt': 168})
    
    

class TestRoute(unittest.TestCase):
    """Test the route testers"""

    def setUp(self):
        self.jobroute = '# OPT'
        self.unknownroute = '# Optimization'
        self.optfreqroute = '# Opt Freq numforce'
        self.twojobroute = '# Opt TS'
        self.oneoptroute = '# opt TZVP'
        self.multijobroute = '# opt b3-lyp TZVP ri marij disp'
        self.multijobslash = '# opt b3-lyp/TZVP ri marij disp'
        self.lowercase = '# def2-tzvp'

    def test_jobroute(self):
        """Test a job"""
        self.assertEqual(check_route(self.jobroute), {'jobtype': 'opt'})

    def test_jobroute(self):
        """Test a job"""
        self.assertEqual(check_route(self.jobroute), {'jobtype': 'opt'})

    def test_oneoptroute(self):
        """Test multiple options"""
        result = {'jobtype': 'opt', 'basis': 'TZVP'}
        self.assertEqual(check_route(self.oneoptroute), result)

    def test_optfreq(self):
        """Test optfreq options"""
        result = {'freqopts': 'numforce', 'jobtype': 'optfreq'}
        self.assertEqual(check_route(self.optfreqroute), result)

    def test_multijobroute(self):
        """Test large amount of options"""
        result = {
            'basis': 'TZVP',
            'disp': True,
            'functional': 'b3-lyp',
            'jobtype': 'opt',
            'marij': True,
            'ri': True
            }
        self.assertEqual(check_route(self.multijobroute), result)

    def test_multijobslash(self):
        """Test with a slash"""
        result = {
            'basis': 'TZVP',
            'disp': True,
            'functional': 'b3-lyp',
            'jobtype': 'opt',
            'marij': True,
            'ri': True
            }
        self.assertEqual(check_route(self.multijobslash), result)

    def test_unknownroute(self):
        """Test an unknown job option"""
        with self.assertRaises(InputCheckError) as cm:
            check_route(self.unknownroute)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg,
                         "Syntax error. Unknown keyword 'Optimization' in route.")

    def test_twojobroute(self):
        """TEst two incompatable job routes"""
        with self.assertRaises(InputCheckError) as cm:
            check_route(self.twojobroute)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg,
                         "More than one jobtype in route. Remove duplicates.")

    def test_lowercaseroute(self):
        """Test a lowercase route"""
        result = {
            'basis': 'def2-TZVP'
        }
        self.assertEqual(check_route(self.lowercase), result)

class TestChSpin(unittest.TestCase):
    """Test the chspin tester"""

    def setUp(self):
        self.good_chspin = '1 2'
        self.neg_chspin = '-1 1'
        self.bad_ch = '12 2'
        self.bad_spin = '1 -2'
        self.too_many_chspin = '0 1 2'

    def test_good_chspin(self):
        """Test a good charge and spin"""
        self.assertEqual(check_chspin(self.good_chspin), {'ch': 1, 'spin': 2})

    def test_neg_chspin(self):
        """Test a negative charge"""
        self.assertEqual(check_chspin(self.neg_chspin), {'ch': -1, 'spin': 1})

    def test_bad_ch(self):
        """Test a bad charge"""
        with self.assertRaises(InputCheckError) as cm:
            check_chspin(self.bad_ch)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, "Illogical molecule charge.")

    def test_bad_spin(self):
        """Test a bad spin"""
        with self.assertRaises(InputCheckError) as cm:
            check_chspin(self.bad_spin)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg,
                         "Spin of -2 is invalid. Requres a positive integer.")

    def test_too_many_chspin(self):
        """Test too many entries"""
        with self.assertRaises(InputCheckError) as cm:
            check_chspin(self.too_many_chspin)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg,
                         "Improper argument for charge and spin.")


class TestGeom(unittest.TestCase):
    """Test the Geometry tester"""

    def setUp(self):
        self.good_geom = ['C 1.000 2.000 -1.000', 'H 2.000 3.000 1.000']
        self.bad_element = ['C 1.000 2.000 -1.000', 'Q 2.000 3.000 1.000']
        self.no_float = ['C 1.000 2.000 -1.000', 'H 2.ooo Help 1.000']

    def test_good_geom(self):
        """Test a good geometry"""
        #NOTE Turbomole uses bohr radius: x//0.52917720859 for geom locations
        result=[
            '1.88972613289 3.77945226577 -1.88972613289 C',
            '3.77945226577 5.66917839866 1.88972613289 H'
            ]
        self.assertEqual(check_geom(self.good_geom), result)

    def test_bad_element(self):
        """Test a non-existant element"""
        with self.assertRaises(InputCheckError) as cm:
            check_geom(self.bad_element)
        the_exception = cm.exception
        self.assertEqual(the_exception.msg,
                         "Input element unknown.")

    def test_no_float(self):
        """Test bad inputs"""
        with self.assertRaises(InputCheckError) as cm:
            check_geom(self.no_float)
        the_exception = cm.exception
        self.assertEqual(
            the_exception.msg,
            "Input geometry should be in cartesian format 'element x y z'."
            )


class TestControlMods(unittest.TestCase):
    """Test the control file modifications. Utilizing testcontrol as filename"""

    def setUp(self):
        self.job = Job()
        self.good_control = [
            '$coord    file=coord',
            '$marij ',
            '$rij',
            '$ricore 500',
            '$rislave 1',
            '$end'
            ]

        write_file('testcontrol', self.good_control)

    def tearDown(self):
        os.remove('testcontrol')

    def test_remove_control(self):
        """Remove something from control file"""
        remove_control(['$marij'], 'testcontrol')
        controlfile = read_clean_file('testcontrol')
        result = [
            '$coord    file=coord',
            '$rij',
            '$ricore 500',
            '$rislave 1',
            '$end'
            ]
        self.assertEqual(controlfile, result)

    def test_remove_multi(self):
        """Remove multiple things from control file"""
        remove_control(['$marij', '$rij'], 'testcontrol')
        controlfile = read_clean_file('testcontrol')
        result = [
            '$coord    file=coord',
            '$ricore 500',
            '$rislave 1',
            '$end'
            ]
        self.assertEqual(controlfile, result)

    def test_add_control(self):
        """Add to control file"""
        add_or_modify_control(['$disp'], 'testcontrol')
        controlfile = read_clean_file('testcontrol')
        result = [
            '$coord    file=coord',
            '$marij',
            '$rij',
            '$ricore 500',
            '$rislave 1',
            '$disp',
            '$end',
            ]
        self.assertEqual(controlfile, result)

    def test_auto_mod_empty(self):
        """Test the auto-modification"""
        self.job.disp = True
        self.job.ri = True
        self.job.jobtype = 'opt'
        self.job.nproc = 4
        result = [
            '$ricore 0',
            '$parallel_parameters maxtask=10000',
            '$paroptions ga_memperproc 900000000000000 900000000000',
            '$ricore_slave 1',
            '$disp',
            '$scfiterlimit 100'
        ]
        self.assertEqual(auto_control_mod(list(), self.job), result)

    def test_auto_mod_mixed(self):
        """Test the automodification with some things already present"""
        self.job.disp = True
        self.job.ri = True
        self.job.jobtype = 'opt'
        self.job.nproc = 4
        result = [
            '$ricore_slave 1',
            '$ricore 0',
            '$parallel_parameters maxtask=10000',
            '$paroptions ga_memperproc 900000000000000 900000000000',
            '$disp',
            '$scfiterlimit 100'
        ]
        precontrol = ['$ricore_slave 1']
        self.assertEqual(auto_control_mod(precontrol, self.job), result)

    def test_freq_job(self):
        """Test for a frequency job"""
        self.job.disp = False
        self.job.ri = False
        self.job.nproc = 1
        self.job.jobtype = 'numforce'
        result = [
            '$maxcor 2048',
            '$parallel_parameters maxtask=10000',
            '$paroptions ga_memperproc 900000000000000 900000000000',
            '$ri',
            '$marij',
            '$ricore 0',
            '$ricore_slave 1'
            ]
        self.assertEqual(auto_control_mod(list(), self.job), result)
    

if __name__ == '__main__':
    unittest.main(verbosity=2)
