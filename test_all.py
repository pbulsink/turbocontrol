#!/usr/bin/env python
"""
Turbogo Main Test Suite

Runs all test files

"""

from unittest import TestLoader, TextTestRunner, TestSuite
from turbogo_test import TestControlEdit, TestJob, TestSetup
from turbogo_test import TestWriteCoord, TestSubmitScriptPrep
from turbogo_helpers_test import TestArgs, TestChSpin
from turbogo_helpers_test import TestControlMods, TestGeom
from turbogo_helpers_test import TestRoute, TestSimpleFuncs
from turbocontrol_test import TestJobset, TestFindInputs
from turbocontrol_test import TestJobChecker, TestWriteStats, TestWriteFreeh
from def_op_test import TestDefine
from screwer_op_test import TestScrewer
from freeh_op_test import TestFreeh
from cosmo_op_test import TestCosmo

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
