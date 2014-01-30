#!/usr/bin/env python
"""Tests what I can of the Turbocontrol Scripts"""

import unittest
import os
from os import path
from turbocontrol import *
from turbogo_helpers import write_file
from turbogo import Job


class TestJobset(unittest.TestCase):
    """Tests the Jobset Class"""
    def setUp(self):
        job = Job()
        self.jobset = Jobset('indir', 'infile', job)

    def test_jobset(self):
        """Make sure the jobset works"""
        self.assertEqual(self.jobset.indir, 'indir')

    def test_jobset_autoname(self):
        """Make sure the auto-name works"""
        name = os.path.join('indir', 'infile')
        self.assertEqual(self.jobset.name, name)


class TestJobChecker(unittest.TestCase):
    """Test the job checking codes"""
    def setUp(self):
        job1 = Job()
        job2 = Job()
        job3 = Job()
        job4 = Job()
        energy = [
'$energy      SCF               SCFKIN            SCFPOT',
'     1 -1508.413363988      1452.770765492     -2961.184129480',
'     2 -1508.439522519      1452.185335264     -2960.624857784',
'     3 -1508.462561108      1451.862821198     -2960.325382306',
'     4 -1508.473774955      1451.769124592     -2960.242899548',
'$end',
        ]
        control = [
'$les all 2',
'$maxcor 2056',
'$orbital_max_rnorm 0.85671291481470E-03',
'$vibrational normal modes',
'  1 1   0.0007426992  -0.0104454972  -0.0430670281   0.0336987972  -0.0954097121',
'  1 2   0.0896161635   0.0053406304  -0.0059127288   0.0005980447   0.0219508437',
'$nvibro      10',
'$vibrational spectrum',
'#  mode     symmetry     wave number   IR intensity    selection rules',
'#                         cm**(-1)        km/mol         IR     RAMAN',
'     1                        0.00         0.00000        -       -',
'     2                        0.00         0.00000        -       -',
'     3                        0.00         0.00000        -       -',
'     4                        0.00         0.00000        -       -',
'     5                        0.00         0.00000        -       -',
'     6                        0.00         0.00000        -       -',
'     7        a              37.01         1.17046       YES     YES',
'     8        a              52.13         1.16835       YES     YES',
'     9        a              54.70         2.04078       YES     YES',
'    10        a              59.99         1.55955       YES     YES',
'$newcoord',
'# cartesian coordinates shifted along normal mode   7 by 5.02923',
'   -8.35953193391576     -0.99142962091868     -1.33326242865311      c',
'   -8.91203963850279     -1.25735534578141      1.24280597454727      c',
'   -6.90739202353972     -0.98927153603955      2.99702881843471      c',
'   -4.41515544700658     -0.47931078232507      2.18251729096911      c',
'$end',
        ]
        controlTS = [
'$les all 2',
'$maxcor 2056',
'$orbital_max_rnorm 0.85671291481470E-03',
'$vibrational normal modes',
'  1 1   0.0007426992  -0.0104454972  -0.0430670281   0.0336987972  -0.0954097121',
'  1 2   0.0896161635   0.0053406304  -0.0059127288   0.0005980447   0.0219508437',
'$nvibro      10',
'$vibrational spectrum',
'#  mode     symmetry     wave number   IR intensity    selection rules',
'#                         cm**(-1)        km/mol         IR     RAMAN',
'     1                        0.00         0.00000        -       -',
'     2                        0.00         0.00000        -       -',
'     3                        0.00         0.00000        -       -',
'     4                        0.00         0.00000        -       -',
'     5                        0.00         0.00000        -       -',
'     6                        0.00         0.00000        -       -',
'     7        a             -37.01         1.17046       YES     YES',
'     8        a              52.13         1.16835       YES     YES',
'     9        a              54.70         2.04078       YES     YES',
'    10        a              59.99         1.55955       YES     YES',
'$newcoord',
'# cartesian coordinates shifted along normal mode   7 by 5.02923',
'   -8.35953193391576     -0.99142962091868     -1.33326242865311      c',
'   -8.91203963850279     -1.25735534578141      1.24280597454727      c',
'   -6.90739202353972     -0.98927153603955      2.99702881843471      c',
'   -4.41515544700658     -0.47931078232507      2.18251729096911      c',
'$end',
        ]
        aoforce = [
'    ------------------------------------------------------------------------',
'         total  cpu-time :   0.48 seconds',
'         total wall-time :   0.57 seconds',
'    ------------------------------------------------------------------------',
'',
'',
'   ****  force : all done  ****',
'',
'',
'    2014-01-09 17:12:15.850',
'',
        ]
        self.jobset1 = Jobset('testdir1', 'testfile', job1, freqopt = 'aoforce')
        self.jobset1.curstart = time()
        self.jobset2 = Jobset('testdir2', 'testfile', job2, freqopt = 'aoforce')
        self.jobset2.curstart = time()
        self.jobset3 = Jobset('testdir3', 'testfile', job3, freqopt = None)
        self.jobset3.curstart = time()
        self.jobset4 = Jobset('testdir4', 'testfile', job4, freqopt = 'aoforce')
        self.jobset4.curstart = time()
        try:
            os.mkdir('testdir1')
            os.mkdir('testdir2')
            os.mkdir('testdir3')
            os.mkdir('testdir4')
        except OSError:
            pass
        turbogo_helpers.write_file(
            os.path.join('testdir1', 'GEO_OPT_CONVERGED'), [''])
        turbogo_helpers.write_file(os.path.join('testdir1', 'energy'), energy)
        turbogo_helpers.write_file(
            os.path.join('testdir1', 'aoforce.out'), aoforce)
        turbogo_helpers.write_file(os.path.join('testdir1', 'control'), control)
        turbogo_helpers.write_file(
            os.path.join('testdir2', 'energy'), ['', '', ''])
        turbogo_helpers.write_file(
            os.path.join('testdir2', 'aoforce.out'),
            ['', '', '', '', '', '', ''])
        turbogo_helpers.write_file(os.path.join(
            'testdir2', 'control'), ['', '', ''])
        turbogo_helpers.write_file(os.path.join(
            'testdir3', 'GEO_OPT_CONVERGED'), [''])
        turbogo_helpers.write_file(os.path.join('testdir3', 'energy'), energy)
        turbogo_helpers.write_file(os.path.join(
            'testdir3', 'aoforce.out'), aoforce)
        turbogo_helpers.write_file(os.path.join(
            'testdir3', 'control'), controlTS)
        turbogo_helpers.write_file(os.path.join(
            'testdir4', 'GEO_OPT_CONVERGED'), [''])
        turbogo_helpers.write_file(os.path.join('testdir4', 'energy'), energy)
        turbogo_helpers.write_file(os.path.join(
            'testdir4', 'aoforce.out'), aoforce)
        turbogo_helpers.write_file(os.path.join('testdir4', 'control'), control)

    def tearDown(self):
        dirlist = ['testdir1', 'testdir2', 'testdir3', 'testdir4']
        filelist = ['GEO_OPT_CONVERGED', 'energy', 'aoforce.out', 'control']
        for directory in dirlist:
            for filename in filelist:
                try:
                    os.remove(path.join(directory, filename))
                except OSError:
                    print "Error with {}".format(path.join(directory, filename))
        try:
            os.rmdir(path.join(os.curdir, 'testdir1'))
            os.rmdir(path.join(os.curdir, 'testdir2'))
            os.rmdir(path.join(os.curdir, 'testdir3'))
            os.rmdir(path.join(os.curdir, 'testdir4'))
        except OSError:
            pass


    def test_check_opt_crashed(self):
        """Check for a crashed optimization"""
        self.assertEqual(check_opt(self.jobset2), 'ocrashed')

    def test_check_opt_complete(self):
        """Check for a completed optimization, no freq"""
        self.assertEqual(check_opt(self.jobset3), 'completed')

    def test_check_freq_crashed(self):
        """Test for a crashed frquency"""
        self.assertEqual(check_freq(self.jobset2), 'fcrashed')

    def test_check_freq_complete(self):
        """Test for a completed frequency, no TS"""
        self.assertEqual(check_freq(self.jobset1), 'completed')

    def test_check_freq_ts_crash(self):
        """Can't test ts resubmit, will crash at qsub command"""
        self.assertEqual(check_freq(self.jobset3), 'ocrashed')

    def test_ensure_not_ts_novib(self):
        """Test for absent vibrations data handling"""
        self.assertEqual(ensure_not_ts(self.jobset2), 'error')

    def test_ensure_not_ts_pass(self):
        """Test for not a TS"""
        self.assertEqual(ensure_not_ts(self.jobset1), 'completed')

    def test_ensure_not_ts_ts(self):
        """Will crash at qsub submit command"""
        self.assertEqual(ensure_not_ts(self.jobset3), 'error')


class TestWriteStats(unittest.TestCase):
    """Test the writing of stats"""
    def setUp(self):
        job1 = Job()
        job2 = Job()
        self.jobset1 = Jobset('testdir1', 'testfile', job1)
        self.jobset1.otime = 600
        self.jobset1.ftime = 3661
        self.jobset1.firstfreq = '50.00'
        self.jobset1.name = 'testjob1'
        self.jobset2 = Jobset('testdir2', 'testfile', job2)
        self.jobset2.otime = 600
        self.jobset2.ftime = 3661
        self.jobset2.firstfreq = '50.00'
        self.jobset2.name = 'testjob2'
        energy = [
'$energy      SCF               SCFKIN            SCFPOT',
'     1 -1508.413363988      1452.770765492     -2961.184129480',
'     2 -1508.439522519      1452.185335264     -2960.624857784',
'     3 -1508.462561108      1451.862821198     -2960.325382306',
'     4 -1508.473774955      1451.769124592     -2960.242899548',
'$end',
        ]
        try:
            os.mkdir('testdir1')
            os.mkdir('testdir2')
        except OSError:
            pass
        turbogo_helpers.write_file(path.join('testdir1','energy'), energy)

    def tearDown(self):
        try:
            os.remove(path.join('testdir1', 'energy'))
            os.rmdir('testdir1')
            os.rmdir('testdir2')
        except OSError:
            pass

    def test_write_stats_no_eng(self):
        """Test for writing stats with energy file missing"""
        answer = ['Name           Directory      Opt Steps   Opt Time   Freq Time   Total Time  1st Frequency       Energy',
                  'testjob2     testdir2/testfile      ?       0:10:00     1:01:01     1:11:01        50.00             ?']
        write_stats(self.jobset2)
        stats = turbogo_helpers.read_clean_file('turbocontrol-stats.txt')
        os.remove('turbocontrol-stats.txt')
        self.assertEqual(stats, answer)

    def test_write_stats_ok(self):
        """Test for ok stats"""
        answer = ['Name           Directory      Opt Steps   Opt Time   Freq Time   Total Time  1st Frequency       Energy',
                  'testjob1     testdir1/testfile      4       0:10:00     1:01:01     1:11:01        50.00      -1508.473774955']
        write_stats(self.jobset1)
        stats = turbogo_helpers.read_clean_file('turbocontrol-stats.txt')
        os.remove('turbocontrol-stats.txt')
        self.assertEqual(stats, answer)


class TestFindInputs(unittest.TestCase):
    """Test Finding inputs"""
    def setUp(self):
        os.mkdir('testdir')
        os.chdir('testdir')
        os.mkdir('indir-good1')
        os.mkdir('indir-good2')
        os.mkdir('indir-badfile3')
        os.mkdir('indir-nofile4')
        os.mkdir('indir-twofile5')
        os.mkdir('indir-deep')
        os.mkdir(os.path.join('indir-deep', 'deepdir'))
        self.infile = """%nproc=8
%mem=100MW
%arch=GA
%maxcycles=200
# Opt ri marij b3-lyp/TZVP

Test Infile

0 1
C -10.14896312689057 1.75782324146904 -0.2949862481115
C -8.99358457406949 2.76561418392812 1.85268749294372
C -6.82890329788933 1.622707823532 2.83855761235287
C -5.82243516371775 -0.51249372509826 1.62856597451948

$ricore 0
$ricore_slave 1
-$marij

"""
        os.chdir('indir-good1')
        write_file('input1.in', self.infile.split('\n'))
        os.chdir(os.pardir)
        os.chdir('indir-good2')
        write_file('input2.in', self.infile.split('\n'))
        os.chdir(os.pardir)
        os.chdir('indir-badfile3')
        write_file('input3.in', ['this is a bad file', 'booya'])
        os.chdir(os.pardir)
        os.chdir('indir-twofile5')
        write_file('input5a.in', self.infile.split('\n'))
        write_file('input5b.in', self.infile.split('\n'))
        os.chdir(os.pardir)
        os.chdir('indir-deep')
        os.chdir('deepdir')
        write_file('input6.in', self.infile.split('\n'))
        os.chdir(os.pardir)
        os.chdir(os.pardir)

    def tearDown(self):
        try:
            os.remove(path.join(path.curdir, 'indir-good1', 'input1.in'))
            os.rmdir(path.join(path.curdir, 'indir-good1'))
        except OSError:
            pass
        try:
            os.remove(path.join(path.curdir, 'indir-good2', 'input2.in'))
            os.rmdir(path.join(path.curdir, 'indir-good2'))
        except OSError:
            pass
        try:
            os.remove(path.join(path.curdir, 'indir-badfile3', 'input3.in'))
            os.rmdir(path.join(path.curdir, 'indir-badfile3'))
        except OSError:
            pass
        try:
            os.rmdir(path.join(path.curdir, 'indir-nofile4'))
        except OSError:
            pass
        try:
            os.remove(path.join(path.curdir, 'indir-twofile5', 'input5a.in'))
            os.remove(path.join(path.curdir, 'indir-twofile5', 'input5b.in'))
            os.rmdir(path.join(path.curdir, 'indir-twofile5'))
        except OSError:
            pass
        try:
            os.remove(path.join(path.curdir, 'indir-deep', 'deepdir', 'input6.in'))
            os.rmdir(path.join(path.curdir, 'indir-deep', 'deepdir'))
            os.rmdir(path.join(path.curdir, 'indir-deep'))
        except OSError:
            pass
        os.chdir(os.pardir)
        try:
            os.rmdir('testdir')
        except OSError:
            pass

    def test_find_inputs(self):
        """Test finding inputs with various problems being handled"""
        codeanswer = find_inputs()
        keys = ['./indir-twofile5', './indir-good2', './indir-deep/deepdir', './indir-good1']
        for key in codeanswer:
            self.assertEqual(isinstance(codeanswer[key][1], Job), True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
