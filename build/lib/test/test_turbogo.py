#!/usr/bin/env python
"""Main Test Suite"""

import unittest
import os
from ..src.turbogo_src import *


class TestJob(unittest.TestCase):
    """Test the job class"""

    def setUp(self):
        self.job = Job()

    def test_disp(self):
        """Make sure auto-dispersion works"""
        job = Job(functional = 'b97-d')
        self.assertEqual(job.disp, True)

    def test_arch(self):
        """Make sure auto-para_arch works"""
        job = Job(jobtype = 'freq')
        self.assertEqual(job.para_arch, 'SMP')


class TestSetup(unittest.TestCase):
    """Test the input file reading & parsing"""

    def setUp(self):
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
        turbogo_helpers.write_file('testinfile.in', self.infile.split('\n'))
        self.job = Job()
        self.job.name = "Test Infile"
        self.job.basis = "TZVP"
        self.job.functional = 'b3-lyp'
        self.job.jobtype = 'opt'
        self.job.iterations = 200
        self.job.charge = 0
        self.job.spin = 1
        self.job.ri = True
        self.job.marij = True
        self.job.disp = None
        self.job.nproc = 8
        self.job.para_arch = 'GA'
        self.job.control_add = ['$ricore 0', '$ricore_slave 1']
        self.job.control_remove = ['$marij']
        self.job.geometry = [
            '-10.14896312689057 1.75782324146904 -0.2949862481115 c',
            '-8.99358457406949 2.76561418392812 1.85268749294372 c',
            '-6.82890329788933 1.622707823532 2.83855761235287 c',
            '-5.82243516371775 -0.51249372509826 1.62856597451948 c',
        ]

    def tearDown(self):
        os.remove('testinfile.in')

    def test_job_setup(self):
        """Make sure name is read properly as proxy for job setup"""
        autojob = jobsetup('testinfile.in')
        self.assertEqual(autojob.name, self.job.name)

    def test_check_file(self):
        """Check a job is returned"""
        self.assertEqual(isinstance(check_input_file('testinfile.in'), Job),
                         True)


class TestWriteCoord(unittest.TestCase):
    """Test the coord writing"""

    def setUp(self):
        self.coordlist = [
            '-10.14896312689057 1.75782324146904 -0.2949862481115 c',
            '-8.99358457406949 2.76561418392812 1.85268749294372 c',
            '-6.82890329788933 1.622707823532 2.83855761235287 c',
            '-5.82243516371775 -0.51249372509826 1.62856597451948 c',
        ]
        self.job = Job()
        self.job.geometry = self.coordlist
        write_coord(self.job, 'testcoord')

    def tearDown(self):
        os.remove('testcoord')

    def test_write_coord(self):
        """Test processing and writing of coordinate file"""
        coordfile = turbogo_helpers.read_clean_file('testcoord')
        result = [
            '$coord',
            '-10.14896312689057 1.75782324146904 -0.2949862481115 c',
            '-8.99358457406949 2.76561418392812 1.85268749294372 c',
            '-6.82890329788933 1.622707823532 2.83855761235287 c',
            '-5.82243516371775 -0.51249372509826 1.62856597451948 c',
            '$end',
            ]
        self.assertEqual(coordfile, result)


class TestControlEdit(unittest.TestCase):
    """Test the multi-control edit cycles"""

    def setUp(self):
        self.job = Job()
        self.good_control = [
            '$coord    file=coord',
            '$marij ',
            '$rij',
            '$disp',
            '$end',
            ]

        turbogo_helpers.write_file('testcontrol', self.good_control)

    def tearDown(self):
        os.remove('testcontrol')

    def test_control_edit(self):
        """Test editing of the control file"""
        self.job.control_add = [
            '$ricore 0',
            '$ricore_slave 1',
            '$marij',
            ]
        self.job.control_remove = [
            '$disp',
        ]
        control_edit(self.job, 'testcontrol')
        result = [
            '$coord    file=coord',
            '$rij',
            '$ricore 0',
            '$ricore_slave 1',
            '$marij',
            '$end',
        ]
        controlfile = turbogo_helpers.read_clean_file('testcontrol')
        self.assertEqual(controlfile, result)


class TestSubmitScriptPrep(unittest.TestCase):
    """Test the submit script generation"""

    def setUp(self):
        self.job1 = Job(ri=True, iterations=300, jobtype='opt', para_arch='MPI',
                        nproc=8, name='Test Job 1')
        submit_script_prepare(self.job1, 'testsubmitscript1')
        self.job2 = Job(ri=True, iterations=300, jobtype='numforce', para_arch='MPI',
                        name='Test Job 2')
        submit_script_prepare(self.job2, 'testsubmitscript2')
        self.job3 = Job(ri=True, iterations=300, jobtype='sp', para_arch='SMP',
                        nproc = 8, name='Test Job 3')
        submit_script_prepare(self.job3, 'testsubmitscript3')
        self.job4 = Job(iterations=300, jobtype='ts', para_arch='GA',
                        nproc=8, name='Test Job 4')
        submit_script_prepare(self.job4, 'testsubmitscript4')

    def tearDown(self):
        os.remove('testsubmitscript1')
        os.remove('testsubmitscript2')
        os.remove('testsubmitscript3')
        os.remove('testsubmitscript4')

    def test_submit_opt(self):
        """Test generation of the submit script"""
        result = [
            '#!/bin/bash',
            '#$ -cwd',
            '#$ -V',
            '#$ -j y',
            '#$ -o test-job-1.stdout',
            '#$ -N tm.test-job-1',
            '#$ -l h_rt=168:00:00',
            '#$ -R y',
            '#$ -pe threaded 8',
            '',
            'export PARA_ARCH=MPI',
            'export MPI_IC_ORDER="TCP"',
            'export PARNODES=7',
            "cat $PE_HOSTFILE | awk '{for(i=0;i<$2;i++) print $1}' > hosts_file",
            'export HOSTS_FILE=`readlink -f hosts_file`',
            '',
            'source $TURBODIR/Config_turbo_env',
            '',
            'ulimit -s unlimited',
            '',
            'touch startfile',
            '',
            'jobex -c 300 -ri > opt.out',
            't2x > optimization.xyz',
            't2x -c > final_geometry.xyz',
            '']
        submitscript = turbogo_helpers.read_clean_file('testsubmitscript1')
        self.assertEqual(submitscript, result)

    def test_submit_numforce(self):
        """Test generation of the submit script"""
        result = [
            '#!/bin/bash',
            '#$ -cwd',
            '#$ -V',
            '#$ -j y',
            '#$ -o test-job-2.stdout',
            '#$ -N tm.test-job-2',
            '#$ -l h_rt=168:00:00',
            '#$ -R y',
            '#$ -pe threaded 1',
            '',
            '',
            'source $TURBODIR/Config_turbo_env',
            '',
            'ulimit -s unlimited',
            '',
            'touch startfile',
            '',
            'NumForce -central -ri > numforce.out',
            '']
        submitscript = turbogo_helpers.read_clean_file('testsubmitscript2')
        self.assertEqual(submitscript, result)

    def test_submit_ts(self):
        """Test generation of the submit script"""
        result = [
            '#!/bin/bash',
            '#$ -cwd',
            '#$ -V',
            '#$ -j y',
            '#$ -o test-job-4.stdout',
            '#$ -N tm.test-job-4',
            '#$ -l h_rt=168:00:00',
            '#$ -R y',
            '#$ -pe threaded 8',
            '',
            'export PARA_ARCH=GA',
            'export MPI_IC_ORDER="TCP"',
            'export PARNODES=8',
            "cat $PE_HOSTFILE | awk '{for(i=0;i<$2;i++) print $1}' > hosts_file",
            'export HOSTS_FILE=`readlink -f hosts_file`',
            '',
            'source $TURBODIR/Config_turbo_env',
            '',
            'ulimit -s unlimited',
            '',
            'touch startfile',
            '',
            'dscf',
            'grad',
            'jobex -trans > ts.out',
            't2x > optimization.xyz',
            't2x -c > final_geometry.xyz',
            '']
        submitscript = turbogo_helpers.read_clean_file('testsubmitscript4')
        self.assertEqual(submitscript, result)

    def test_submit_sp(self):
        """Test generation of the submit script"""
        result = [
            '#!/bin/bash',
            '#$ -cwd',
            '#$ -V',
            '#$ -j y',
            '#$ -o test-job-3.stdout',
            '#$ -N tm.test-job-3',
            '#$ -l h_rt=168:00:00',
            '#$ -R y',
            '#$ -pe threaded 8',
            '',
            'export PARA_ARCH=SMP',
            'export MPI_IC_ORDER="TCP"',
            'export PARNODES=8',
            "cat $PE_HOSTFILE | awk '{for(i=0;i<$2;i++) print $1}' > hosts_file",
            'export HOSTS_FILE=`readlink -f hosts_file`',
            '',
            'source $TURBODIR/Config_turbo_env',
            '',
            'ulimit -s unlimited',
            '',
            'touch startfile',
            '',
            'ridft > sp.out',
            '']
        submitscript = turbogo_helpers.read_clean_file('testsubmitscript3')
        self.assertEqual(submitscript, result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
