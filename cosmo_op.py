
#!/usr/bin/env python
"""
Turbogo has to call cosmoprep. Cosmoprep is a huge mess of pexpect calls and
expectations, it is broken out here for isolation purposes and to track
differences between changes to the turbogo file and adjustments to cosmo case
handling.
Calls expect a job. Not a standalone script. Called only from turbogo.py
"""

import pexpect  # pragma: no cover
import logging
import os
import turbogo_helpers

TURBODIR=os.getenv('TURBODIR')
TURBOSYS=os.getenv('TURBOMOLE_SYSNAME')
if not TURBOSYS:
    TURBOSYS = 'em64t-unknown-linux-gnu'
if TURBODIR:
    TURBOSCRIPT = os.path.join(TURBODIR, 'bin', TURBOSYS)
else:
    TURBOSCRIPT = ''

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class CosmoError(Error):
    """
    General Exception for cosmoprep errors
    Attributes:
        value = exception value passed through
    """

    def __init__(self, value):
        self.value = value


class Cosmo():
    """Make cosmo a callable object"""

    def __init__(self, timeout=60):
        """
        Start a cosmoprep object for specified job with optional timeout
        modification (in seconds)
        """
        self.timeout = timeout
        logging.debug("Cosmoprep instance initiated")

    def setup_cosmo(self, job):
        """Set up the parameters for a cosmoprep job"""
        self.make_parameters(job)

    def start_cosmo(self):
        """Spawns a cosmoprep instance, with optional logfile tracking"""
        try:
            self.cosmo = pexpect.spawn("cosmoprep")
        except Exception as e:
            try:
                self.cosmo = pexpect.spawn(os.path.join(TURBOSCRIPT, 'cosmoprep'))
            except Exception as e:
                raise CosmoError(
                    "Error starting cosmoprep: {} Check the environment is set up".format(
                    str(e)))
            else:
                logging.debug("Environment not loaded. cosmoprep loaded manually.")
        else:
            logging.debug("Cosmoprep instance spawned and active.")

        self.cosmo.timeout = self.timeout
        fout = file('cosmolog.txt','w')
        self.cosmo.logfile = fout

    def make_parameters (self, job):
        """Convert job parameters into cosmoprep parameters"""
        try:
            if turbogo_helpers.is_positive_float(job.cosmo):
                self.epsilon = job.cosmo
            else:
                #cosmo can be called with infinite epsilon (default)
                self.epsilon = ''
            logging.debug('parameters made')
        except Exception as e:
            self.epsilon = ''
            logging.warn("Error in make_parameters: {}".format(e))

    def run_cosmo(self):
        """Run cosmo depending on parameters list"""
        try:
            out = self.cosmo.expect([
                'Keyword $cosmo already exists',
                'epsilon'
                ])
            if out == 0:
                self.cosmo.sendline('d')
                logging.debug('Cleared old cosmo data')
            if self.epsilon and turbogo_helpers.is_positive_float(self.epsilon):
                self.cosmo.sendline(self.epsilon)
                logging.debug('Epsilon of {} set'.format(self.epsilon))
            else:
                self.cosmo.sendline('')
                logging.debug('Default epsilon set')
            #lots of opportunity to expand cosmo interaction here
            self.cosmo.expect('refind')
            self.cosmo.sendline('')
            self.cosmo.expect('LR terms on')
            self.cosmo.sendline('')
            self.cosmo.expect('COSMO RF equil. is not set')
            self.cosmo.sendline('')
            self.cosmo.expect('nppa')
            self.cosmo.sendline('')
            self.cosmo.expect('nspa')
            self.cosmo.sendline('')
            self.cosmo.expect('disex')
            self.cosmo.sendline('')
            self.cosmo.expect('rsolv')
            self.cosmo.sendline('')
            self.cosmo.expect('routf')
            self.cosmo.sendline('')
            self.cosmo.expect('cavity')
            self.cosmo.sendline('')
            self.cosmo.expect('amat')
            self.cosmo.sendline('')
            self.cosmo.expect('if radius is in Bohr units append b')
            self.cosmo.sendline('r all b')
            self.cosmo.sendline('*')
            self.cosmo.expect('COSMO output file')
            self.cosmo.sendline('')
            self.cosmo.expect('y/n, default = n')
            self.cosmo.sendline('')
        except Exception as e:
            logging.warn('Cosmo Error: {}'.format(e))
            raise CosmoError('Error in running cosmoprep. Error: {}'.format(e))

        exitcode = self._end_cosmo()
        return exitcode


    def _end_cosmo(self):
        """close cosmo, first graceful then forced"""
        try:
            self.cosmo.wait()
            logging.debug('Cosmoprep ended successfully.')
        except:

            try:
                self.cosmo.close()
            except:
                logging.warning("Cosmoprep isn't closing correctly.")

                try:
                    self.cosmo.close(force=True)
                except:
                    logging.critical("Cosmoprep isn't closing with force.")

        try:
            if self.cosmo.signalstatus:
                logging.debug('signalstatus: {}'.format(self.cosmo.signalstatus))
                return self.cosmo.signalstatus
            if self.cosmo.exitstatus:
                logging.debug('exitstatus: {}'.format(self.cosmo.exitstatus))
                return self.cosmo.exitstatus
        except:
            return -99


if __name__ == "__main__":
    print "Not a callable script. Please run Turbogo or TurboControl."
    exit()
