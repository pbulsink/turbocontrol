#!/usr/bin/env python
"""
Turbogo has to call define. Define is a huge mess of pexpect calls and
expectations, it is broken out here for isolation purposes and to track
differences between changes to the turbogo file and adjustments to define case
handling.
Calls expect a job. Not a standalone script. Called only from turbogo.py
"""

import pexpect  # pragma: no cover
import logging
import time
import os

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

class DefineError(Error):
    """
    General Exception for define errors
    Attributes:
        value = exception value passed through
    """

    def __init__(self, value):
        self.value = value


class Define():
    """Make define a callable object"""

    def __init__(self, timeout=60):
        """
        Start a define object for specified job with optional timeout
        modification (in seconds)
        """
        self.timeout = timeout
        logging.debug("Define instance initiated")

    def setup_define(self, job):
        """Set up the parameters for a define job"""
        self.make_parameters(job)

    def start_define(self):
        """Spawns a define instance, with optional logfile tracking"""
        try:
            self.define = pexpect.spawn("define")
        except Exception as e:
            try:
                self.define = pexpect.spawn(os.path.join(TURBOSCRIPT, 'define'))
            except Exception as e:
                raise DefineError(
                    "Error starting Define {}. Check the environment is set up".format(
                    str(e)))
            else:
                logging.debug("Environment not loaded. Define loaded manually.")
        else:
            logging.debug("Define instance spawned and active.")

        self.define.timeout = self.timeout
        fout = file('mylog.txt','w')
        self.define.logfile = fout

    def make_parameters (self, job):
        """Convert job parameters into define parameters"""
        self.title = job.name
        self.gparams = dict()
        self.bparams = dict()
        self.eparams = dict()
        self.fparams = dict()

        #These are dictionaries to be expandable as further regions of define
        #get explored.
        self.gparams['charge'] = job.charge
        self.bparams['basis'] = job.basis
        self.eparams['charge'] = job.charge
        self.eparams['spin'] = job.spin

        if job.ri:
            self.fparams['ri'] = True
            self.fparams['m'] = 3200
        if job.marij:
            self.fparams['marij'] = True
        if job.jobtype == 'ts':
            self.gparams['jobtype'] = 'ts'
        elif job.jobtype == 'sp':
            self.gparams['jobtype'] = 'sp'
        else:
            self.gparams['jobtype'] = 'freqopt'
        self.fparams['func'] = job.functional

    def run_define(self):
        """Run define depending on parameters list"""
        self._write_title(self.title)
        self._geom()
        self._next("geom")
        self._basis()
        self._next("basis")
        self._electronic()
        self._functional()
        self._next("general")
        exitcode = self._end_define()
        return exitcode

    def _write_title(self, title):
        """Progress to finished writing title of job"""
        try:
            out = self.define.expect([
                'FILE control ALREADY EXISTS',
                'DATA WILL BE WRITTEN TO THE NEW FILE control'
                ])
            if out == 0:
                #some files exist. Not a clean directory
                self.clean = False
                logging.debug('Directory is not clean. Control file exists.')
            elif out == 1:
                #Clean Directory
                self.clean = True
                logging.debug('Directory is clean from control file.')
            else:
                logging.warning('Unexpected response from define.')
                raise DefineError('Unexpected response in define: control file')
            self.define.sendline('')

            self.define.expect(['INPUT TITLE OR'])
            self.define.sendline(title)
            logging.debug('Title written.')

            #Check for old geometry & erase
            out = self.define.expect(['DO YOU WANT TO CHANGE THE GEOMETRY DATA',
                                      'SPECIFICATION OF MOLECULAR GEOMETRY'])
            if out == 0:
                self.define.sendline('y')
                self.define.sendline('del all')
                out = self.define.expect(['CONFIRM REMOVAL OF THESE'])
                if out == 0:
                    self.define.sendline('y')
                    logging.debug('Old Geometry cleared')

        except Exception as e:
            raise DefineError(
                'Error in preparing control & title. Error: {}'.format(e)
                )

    def _geom(self):
        """Work in the geometry menu"""
        try:
            #a coord
            self.define.sendline('a coord')
            self.define.expect('CARTESIAN COORDINATES FOR ')
            logging.debug('Coordinates imported.')
            if self.gparams['jobtype'] != 'ts' or self.gparams['jobtype'] != 'sp':
                #uff
                self.define.expect('IF YOU APPEND A QUESTION MARK TO ANY COMMAND')
                self.define.sendline('ff')
                self.define.expect('Enter UFF-options to be modified')
                if 'charge' in self.gparams:
                    self.define.sendline('c ' + str(self.gparams['charge']))
                self.define.sendline('')
                self.define.expect('UFF ended normally')
                logging.debug('Uff done.')
                #desy
                self.define.expect('IF YOU APPEND A QUESTION MARK TO ANY COMMAND')
                self.define.sendline('desy')
                self.define.expect('symmetry operations found')
                logging.debug('Desy done.')
                #ired
                self.define.expect('IF YOU APPEND A QUESTION MARK TO ANY COMMAND')
                self.define.sendline('ired')
                logging.debug('Ired done.')
            logging.debug('Geometry setup complete.')
        except Exception as e:
            raise DefineError('Error in setting up geometry. Error {}'.format(e))

    def _basis(self):
        """Work in the basis menu"""
        #b all {{basis}}
        try:
            self.define.sendline('b all {}'.format(self.bparams['basis']))
        except Exception as e:
            raise DefineError('Error in setting basis set. Error {}'.format(e))
        logging.debug("Basis sets applied.")

    def _electronic(self):
        """work in the MO & electronic configuration menu"""
        try:

            self.define.sendline('eht')
            logging.debug('Eht Started.')
            out = self.define.expect(['DO YOU WANT THE DEFAULT PARAMETERS FOR THE EXTENDED HUECKEL CALCULATION'])
            if out == 0:
                self.define.sendline('')
                out = self.define.expect(['ENTER THE '])
                if out == 0:
                    self.define.sendline(str(self.eparams['charge']))
                    logging.debug('Charge applied.')
                    out = self.define.expect([
                        'DO YOU ACCEPT THIS OCCUPATION',
                        'DO YOU WANT THE DEFAULT OCCUPATION'])
                    if out == 0:
                        if self.eparams['spin'] == 1:
                            self.define.sendline('')
                        else: #Any other spin (as int) applied
                            self.define.sendline('n')
                            self.define.expect('ENTER COMMAND')
                            self.define.sendline('u {}'
                                                 .format(int(
                                                    self.eparams['spin'])-1))
                            self.define.expect('ENTER COMMAND')
                            self.define.sendline('*')
                        logging.debug('Spin of {} applied.'
                                      .format(self.eparams['spin']))
                        out = self.define.expect([
                            'LEFT OVER FROM PREVIOUS CALCULATIONS',
                            'GENERAL MENU'])
                        if out == 0:
                            self.define.sendline('')
                            logging.debug('Leftover Files accepted.')
                            out = self.define.expect([
                                'DO YOU REALLY WANT TO WRITE OUT NATURAL ORBITALS',
                                'GENERAL MENU'
                            ])
                            if out == 0:
                                self.define.sendline('')
                                logging.debug('Natural orbitals not written')
                        else:
                            logging.debug('No leftover files to accept.')
                    else:
                        self.define.sendline('')
                        out = self.define.expect([
                            'LEFT OVER FROM PREVIOUS CALCULATIONS',
                            'LIST OF MO-SHELL INDICES',
                            'GENERAL MENU'])
                        if out == 0:
                            self.define.sendline('')
                            logging.debug('Leftover Files accepted.')
                            out = self.define.expect([
                                'DO YOU REALLY WANT TO WRITE OUT NATURAL ORBITALS',
                                'GENERAL MENU'
                            ])
                            if out == 0:
                                self.define.sendline('')
                                logging.debug('Natural orbitals not written')
                        elif out == 1:
                            self.define.sendline('u {}'.format(int(self.eparams['spin'])-1))
                            self.define.sendline('*')
                            out = self.define.expect([
                            'LEFT OVER FROM PREVIOUS CALCULATIONS',
                            'GENERAL MENU'])
                            if out == 0:
                                self.define.sendline('')
                                logging.debug('Leftover Files accepted.')
                                out = self.define.expect([
                                    'DO YOU REALLY WANT TO WRITE OUT NATURAL ORBITALS',
                                    'GENERAL MENU'
                                ])
                                if out == 0:
                                    self.define.sendline('')
                                    logging.debug('Natural orbitals not written')
                        else:
                            logging.debug('No leftover files to accept.')
        except Exception as e:
            raise DefineError('Error in electronic and MO configuration. Error {}'.format(e))
        logging.debug('MO and Electronic information applied.')


    def _functional(self):
        """Work in the functional menu"""
        #dft
        self._dft()
        logging.debug('DFT done.')
        if 'ri' in self.fparams:
            self._ri()
            logging.debug('RI done.')
        if 'marij' in self.fparams:
            self._marij()
            logging.debug('MARIJ done.')
        if self.gparams['jobtype'] == 'ts':
            self._stp()
            logging.debug('STP modified for TS job')
        logging.debug('Functional paramters applied.')

    def _dft(self):
        """Work in the dft menu"""
        try:
            self.define.expect("END OF DEFINE")
            self.define.sendline('dft')
            #func
            logging.debug('Selecting func {}'.format(self.fparams['func']))
            self.define.expect("ENTER DFT-OPTION TO BE MODIFIED")
            self.define.sendline('func {}'.format(self.fparams['func']))
            self.define.expect('functional {}'.format(self.fparams['func']))
            logging.debug('Func selected.')
            #on
            self.define.sendline('on')
            self.define.expect('DFT is used')
            logging.debug('DFT turned on.')
            self.define.sendline('')
        except Exception as e:
            raise DefineError('Error in dft preparation. Error {}'.format(e))

    def _ri(self):
        """Work in the RI menu"""
        try:
            self.define.expect("END OF DEFINE")
            self.define.sendline('ri')
            self.define.expect("ENTER RI-OPTION TO BE MODIFIED")
            self.define.sendline('m {}'.format(self.fparams['m']))
            logging.debug('RI Memory set at {}.'.format(self.fparams['m']))
            self.define.sendline('on')
            self.define.expect("RI IS USED")
            logging.debug('RI on.')
            self.define.sendline('')
        except Exception as e:
            raise DefineError('Error in ri preparation. Error {}'.format(e))

    def _marij(self):
        """Work in the MARIJ menu"""
        try:
            self.define.expect("END OF DEFINE")
            self.define.sendline('marij')
            self.define.expect('Enter the number to change a value or <return> to accept all')
            self.define.sendline('')
            logging.debug('MARIJ on')
        except Exception as e:
            raise DefineError('Error in marij preparation. Error {}'.format(e))

    def _stp(self):
        """Work the STP menu"""
        try:
            self.define.expect("END OF DEFINE")
            self.define.sendline('stp')
            self.define.expect("ENTER STATPT-OPTIONS TO BE MODIFIED")
            self.define.sendline('on')
            self.define.expect("ENTER STATPT-OPTIONS TO BE MODIFIED")
            self.define.sendline('itvc')
            self.define.expect("Enter index of transition vector.")
            self.define.sendline('1')
            self.define.sendline('')
            logging.debug('STP set with itvc = 1')
        except Exception as e:
            raise DefineError('Error in STP prepareation. Error {}'.format(e))
    

    def _next(self, leaving = None):
        """
        Pass the next menu command to define, maybe checking for passed result
        """
        if leaving == 'geom':
            try:
                self.define.sendline('*')
                logging.debug('* sent to leave geom')
                out = self.define.expect(['DO YOU WANT TO CHANGE THESE DATA', 'IF YOU DO NOT WANT TO USE INTERNAL COORDINATES ENTER  no', 'ATOMIC ATTRIBUTE DEFINITION MENU'])
                if out == 0:
                    self.define.sendline('y')
                    logging.debug('Atomic attribute data overwrite selected')
                    out = self.define.expect('ATOMIC ATTRIBUTE DEFNIITION DATA')
                elif out == 1:
                    self.define.sendline('no')
                    logging.debug('Do not use internal coordinate selected')
                    out = self.define.expect(' GOBACK=& (TO GEOMETRY MENU !)')
                elif out == 2:
                    logging.debug('In Atomic Attribute Menu')
            except Exception as e:
                raise DefineError('Error in moving to basis. Error {}'.format(e))
        elif leaving == 'basis':
            try:
                self.define.sendline('*')
                logging.debug('* sent to leave basis')
                out = self.define.expect('MOLECULAR ORBITAL DEFINITION MENU')
            except Exception as e:
                raise DefineError('Error in moving to electronic and MO menu. Error {}'.format(e))
        elif leaving == 'general':
            try:
                self.define.sendline('*')
                logging.debug('* sent to leave general menu')
            except Exception as e:
                raise DefineError('Error in moving to next menu. Error {}'.format(e))
        else:
            try:
                self.define.sendline('*')
                logging.debug ('* sent to leave menu')
            except Exception as e:
                raise DefineError('Error in moving to next menu. Error {}'.format(e))
        logging.debug('Next menu successfully requested.')

    def _end_define(self):
        """close define, first graceful then forced"""
        try:
            self.define.wait()
            logging.debug('Define ended successfully.')
        except:

            try:
                self.define.close()
            except:
                logging.warning("Define isn't closing correctly.")

                try:
                    self.define.close(force=True)
                except:
                    logging.critical("Define isn't closing with force.")

        try:
            if self.define.signalstatus:
                logging.debug('signalstatus: {}'.format(self.define.signalstatus))
                return self.define.signalstatus
            if self.define.exitstatus:
                logging.debug('exitstatus: {}'.format(self.define.exitstatus))
                return self.define.exitstatus
        except:
            return -99


if __name__ == "__main__":
    print "Not a callable script. Please run Turbogo or TurboControl."
    exit()
