#!/usr/bin/env python
"""Tests what I can of the Turbocontrol Scripts"""

import unittest
import os
from os import path
from turbocontrol.turbocontrol import *
from turbocontrol.utilities.turbogo_helpers import write_file
from turbocontrol.turbogo import Job




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
        job1 = Job(indir='testdir1', infile='testfile')
        job2 = Job(indir='testdir2', infile='testfile')
        job3 = Job(indir='testdir3', infile='testfile', jobtype = 'opt')
        job4 = Job(indir='testdir4', infile='testfile')
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
        controldoubleTS = [
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
'     8        a             -52.13         1.16835       YES     YES',
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
        self.jobset1 = Jobset('testdir1', 'testfile', job1)
        self.jobset1.job.curstart = time()
        self.jobset1.job.freqopt='aoforce'
        self.jobset2 = Jobset('testdir2', 'testfile', job2)
        self.jobset2.job.curstart = time()
        self.jobset2.job.freqopt=None
        self.jobset3 = Jobset('testdir3', 'testfile', job3, freqopt = None)
        self.jobset3.job.curstart = time()
        self.jobset3.job.freqopt=None
        self.jobset4 = Jobset('testdir4', 'testfile', job4)
        self.jobset4.job.curstart = time()
        self.jobset4.job.freqopt='aoforce'
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
            'testdir2', 'control'), controldoubleTS)
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
        self.assertEqual(check_opt(self.jobset2.job), 'ocrashed')

    def test_check_opt_complete(self):
        """Check for a completed optimization, no freq"""
        self.assertEqual(check_opt(self.jobset3.job), 'completed')

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

    def test_ensure_ts_ts(self):
        """Test to ensure job is a ts"""
        self.assertEqual(ensure_ts(self.jobset2), 'imaginary')

    def test_ensure_ts_not_ts(self):
        """Woops solved a stable state"""
        self.assertEqual(ensure_ts(self.jobset1), 'opt')

    def test_ensure_ts_double(self):
        """Got an imaginary. Thsi shouldn't happen"""
        self.assertEqual(ensure_ts(self.jobset3), 'ts')
    

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
        stats = turbogo_helpers.read_clean_file('stats.txt')
        os.remove('stats.txt')
        self.assertEqual(stats, answer)

    def test_write_stats_ok(self):
        """Test for ok stats"""
        answer = ['Name           Directory      Opt Steps   Opt Time   Freq Time   Total Time  1st Frequency       Energy',
                  'testjob1     testdir1/testfile      4       0:10:00     1:01:01     1:11:01        50.00      -1508.473774955']
        write_stats(self.jobset1)
        stats = turbogo_helpers.read_clean_file('stats.txt')
        os.remove('stats.txt')
        self.assertEqual(stats, answer)

class TestWriteFreeh(unittest.TestCase):
    """Test the writing of freeh"""
    def setUp(self):
        data1 = {'zpe': '481.3', 't': ['298.15'], 'p': ['0.1000000'],
                 'qtrans': ['19.81'], 'qrot': ['15.66'], 'qvib': ['15.89'],
                 'pot': ['353.99'], 'eng': ['530.06'], 'entr': ['0.59886'],
                 'cv': ['0.2849985'], 'cp': ['0.2933128'], 'enth': ['532.54']}
        data2 = {'zpe': '481.3', 't': ['298.15', '308.15', '318.15'],
                 'p': ['0.1000000', '0.1000000', '0.1000000'],
                 'qtrans': ['19.81', '20.81', '21.81'],
                 'qrot': ['15.66', '16.66', '17.66'],
                 'qvib': ['15.89', '16.89', '17.89'],
                 'pot': ['353.99', '363.99', '373.99'],
                 'eng': ['530.06', '540.06', '550.06'],
                 'entr': ['0.59886', '0.60886', '0.61886'],
                 'cv': ['0.2849985', '0.2949985', '0.3049985'],
                 'cp': ['0.2933128', '0.3033128', '0.3133128'],
                 'enth': ['532.54', '542.54', '552.54']}
        self.job1 = Job(data=data1, name='testjob1', indir='testdir1', infile = 'infile1')
        self.job2 = Job(data=data2, name='testjob2', indir='testdir2', infile = 'infile2')
        self.headerstring = ("{name:^16}{directory:^20}{zpe:^14}{t:^10}" \
                        "{p:^11}{qtrans:^12}{qrot:^10}" \
                        "{pot:^14}{eng:^14}{entr:^20}{cv:^14}{cp:^14}{enth:^14}"
                        .format(
                            name='Name',
                            directory = 'Directory',
                            zpe = 'ZPE (kJ/mol)',
                            t = 'Temp (K)',
                            p = 'p (MPa)',
                            qtrans = 'ln(qtrans)',
                            qrot = 'ln(qrot)',
                            qvib = 'ln(qvib)',
                            pot = 'Pot (kJ/mol)',
                            eng = 'Eng (kJ/mol)',
                            entr = 'Entropy (kJ/mol/K)',
                            cv = 'Cv (kJ/molK)',
                            cp = 'Cp (kJ/molK)',
                            enth = 'Enthalpy (kJ/mol)'
                        ))

    def tearDown(self):
        try:
            os.remove('freeh.text')
            os.remove('freeh')
        except OSError:
            pass
    
    def test_write_freeh(self):
        """Test for writing stats with energy file missing"""
        answer = ['Name           Directory       ZPE (kJ/mol)  Temp (K)   p (MPa)   ln(qtrans)  ln(qrot)  Pot (kJ/mol)  Eng (kJ/mol)  Entropy (kJ/mol/K)  Cv (kJ/molK)  Cp (kJ/molK) Enthalpy (kJ/mol)',
                  'testjob1      testdir1/infile1      481.3       298.15   0.1000000    19.81      15.66       353.99        530.06          0.59886         0.2849985     0.2933128       532.54']
        write_freeh(self.job1)
        freeh = turbogo_helpers.read_clean_file('freeh.txt')
        os.remove('freeh.txt')
        self.assertEqual(freeh, answer)
    
    def test_write_multi_freeh(self):
        """Test for ok stats"""
        answer = ['Name           Directory       ZPE (kJ/mol)  Temp (K)   p (MPa)   ln(qtrans)  ln(qrot)  Pot (kJ/mol)  Eng (kJ/mol)  Entropy (kJ/mol/K)  Cv (kJ/molK)  Cp (kJ/molK) Enthalpy (kJ/mol)',
                  'testjob2      testdir2/infile2      481.3       298.15   0.1000000    19.81      15.66       353.99        530.06          0.59886         0.2849985     0.2933128       532.54',
                  '308.15  0.1000000    20.81      16.66       363.99        540.06          0.60886         0.2949985     0.3033128       542.54',
                  '318.15  0.1000000    21.81      17.66       373.99        550.06          0.61886         0.3049985     0.3133128       552.54']
        write_freeh(self.job2)
        freeh = turbogo_helpers.read_clean_file('freeh.txt')
        os.remove('freeh.txt')
        self.assertEqual(freeh, answer)
    
    def test_write_freeh_preexisting(self):
        answer = ['Name           Directory       ZPE (kJ/mol)  Temp (K)   p (MPa)   ln(qtrans)  ln(qrot)  Pot (kJ/mol)  Eng (kJ/mol)  Entropy (kJ/mol/K)  Cv (kJ/molK)  Cp (kJ/molK) Enthalpy (kJ/mol)',
                  'testjob1      testdir1/infile1      481.3       298.15   0.1000000    19.81      15.66       353.99        530.06          0.59886         0.2849985     0.2933128       532.54']
        turbogo_helpers.write_file('freeh.txt', self.headerstring.split('\n'))
        write_freeh(self.job1)
        freeh = turbogo_helpers.read_clean_file('freeh.txt')
        os.remove('freeh.txt')
        self.assertEqual(freeh, answer)
    


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
