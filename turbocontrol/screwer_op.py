#!/usr/bin/env python
"""
Turbocontrol may have to call screwer if the optimization is a TS.
In the form of def_op, screwer is an interactive script. It has been broken
from the general script to track differences between changes to the turbocontrol
file and adjustments to screwer case handling.
Calls expect a job. Not a standalone script. Called only from turbocontrol.py
"""

import pexpect  # pragma: no cover
import logging
import time
import os

TURBODIR=os.getenv('TURBODIR')
if TURBODIR:
    TURBOSCRIPT = os.path.join(TURBODIR, 'bin', 'em64t-unknown-linux-gnu')
else:
    TURBOSCRIPT = ''

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ScrewerError(Error):
    """
    General Exception for screwer errors
    Attributes:
        value = exception value passed through
    """

    def __init__(self, value):
        self.value = value


class NoVibError(Error):
    """
    Exception for no vibrational modes found in directory
    Attributes:
        msg = error message
    """

    def __init__(self, msg):
        self.msg = msg

class ModeError(Error):
    """
    Exception for a bad mode (ie. translation only)
    Attributes:
        msg = error message
    """

    def __init__(self, msg):
        self.msg = msg

class Screwer():
    """Makes a callable object"""

    def __init__(self, mode, timeout = 60):
        """
        Starts a screwer with optional timeout modification in seconds
        """
        self.timeout = timeout
        self.mode = mode
        logging.debug("Screwer started")

    def run_screwer(self):
        """
        Runs screwer
        """
        try:
            self.screwer = pexpect.spawn("screwer")
        except Exception as e:
            try:
                self.screwer = pexpect.spawn(os.path.join(TURBOSCRIPT, 'screwer'))
            except Exception as e:
                raise ScrewerError(
                    "Error starting screwer {}. Check the environment is set up".format(
                    str(e)))
            else:
                logging.debug("Environment not set up. Manually loaded screwer")
        else:
            logging.debug("Screwer instance spawned and active.")

        self.screwer.timeout = self.timeout

        out = self.screwer.expect([
            ' $vibrational normal modes not found',
            ' ALONG WHICH MODE COORDINATES SHOULD BE SHIFTED'
        ])
        if out == 0:
            #Not a valid directory to run screwer in
            logging.debug("No vibrational modes found in directory.")
            raise NoVibError("No vibrational modes found in directory.")

        self.screwer.sendline(self.mode)
        out = self.screwer.expect([
            '!!! Try once again !!! ',
            'INPUT STEP LENGTH'
        ])
        if out == 0:
            logging.debug("Bad mode, can't shift along this vibration.")
            raise ModeError("Bad mode, not valid for vibrational shifting.")
        self.screwer.sendline('')
        self._end_screwer

    def _end_screwer(self):
        """close screwer, first graceful then forced"""
        try:
            self.screwer.wait()
            logging.debug('Screwer ended successfully.')
        except:

            try:
                self.screwer.close()
            except:
                logging.warning("Screwer isn't closing correctly.")

                try:
                    self.screwer.close(force=True)
                except:
                    logging.critical("Screwer isn't closing with force.")

        try:
            if self.screwer.signalstatus:
                logging.debug('signalstatus: {}'.format(self.screwer.signalstatus))
                return self.screwer.signalstatus
            if self.screwer.exitstatus:
                logging.debug('exitstatus: {}'.format(self.screwer.exitstatus))
                return self.screwer.exitstatus
        except:
            return -99

if __name__ == "__main__":
    print "Not a callable script. Please run Turbogo or TurboControl."
    exit()
