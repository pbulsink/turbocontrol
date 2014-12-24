#!/usr/bin/env python
"""Functions to get the correct sympy version to run tests."""

import os
import sys

def path_hack():
    """
    Hack sys.path to import correct (local) turbocontrol.
    """
    this_file = os.path.abspath(__file__)
    turbocontrol_dir = os.path.join(os.path.dirname(this_file), "..")
    turbocontrol_dir = os.path.normpath(sympy_dir)
    sys.path.insert(0, turbocontrol_dir)
    return turbocontrol_dir
