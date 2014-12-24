#!/usr/bin/env python
"""
Turbogo Main Test Suite

Runs all test files

"""

from unittest import TestLoader, TextTestRunner, TestSuite
from test_turbogo import TestControlEdit, TestJob, TestSetup
from test_turbogo import TestWriteCoord, TestSubmitScriptPrep
from test_turbogo_helpers import TestArgs, TestChSpin
from test_turbogo_helpers import TestControlMods, TestGeom
from test_turbogo_helpers import TestRoute, TestSimpleFuncs
from test_turbocontrol import TestJobset, TestFindInputs
from test_turbocontrol import TestJobChecker, TestWriteStats, TestWriteFreeh
from test_def_op import TestDefine
from test_screwer_op import TestScrewer
from test_freeh_op import TestFreeh
from test_cosmo_op import TestCosmo

if __name__ == "__main__":
    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(TestControlEdit),
        loader.loadTestsFromTestCase(TestJob),
        loader.loadTestsFromTestCase(TestSetup),
        loader.loadTestsFromTestCase(TestWriteCoord),
        loader.loadTestsFromTestCase(TestSubmitScriptPrep),
        loader.loadTestsFromTestCase(TestArgs),
        loader.loadTestsFromTestCase(TestChSpin),
        loader.loadTestsFromTestCase(TestControlMods),
        loader.loadTestsFromTestCase(TestGeom),
        loader.loadTestsFromTestCase(TestRoute),
        loader.loadTestsFromTestCase(TestSimpleFuncs),
        loader.loadTestsFromTestCase(TestJobset),
        loader.loadTestsFromTestCase(TestFindInputs),
        loader.loadTestsFromTestCase(TestJobChecker),
        loader.loadTestsFromTestCase(TestWriteStats),
        loader.loadTestsFromTestCase(TestDefine),
        loader.loadTestsFromTestCase(TestScrewer),
        loader.loadTestsFromTestCase(TestFreeh),
        loader.loadTestsFromTestCase(TestCosmo),
        loader.loadTestsFromTestCase(TestWriteFreeh),
        ))

    runner = TextTestRunner(verbosity = 2)
    runner.run(suite)
