#!/usr/bin/env python
"""
Turbomole inclues a script called freeh to get energy values from completed
vibrational analysis jobs. This is another interactive script.
This will work through freeh and get energies back, at standard or alternate
pressures, tempearatures, or other modifiable environments.
"""

import pexpect  # pragma: no cover
import logging
import time
import os
import turbogo_helpers

TURBODIR=os.getenv('TURBODIR')
if TURBODIR:
    TURBOSCRIPT = os.path.join(TURBODIR, 'bin', 'em64t-unknown-linux-gnu')
else:
    TURBOSCRIPT = ''

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class FreehError(Error):
    """
    General Exception for freeh errors
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


class Freeh():
    """Makes a callable object"""

    def __init__(self, modvals = '', timeout = 60):
        """
        Starts a freeh with optional timeout modification in seconds
        """
        self.timeout = timeout
        self.scale = ''
        self.tstart = ''
        self.tend = ''
        self.numt = ''
        self.pstart = ''
        self.pend = ''
        self.nump = ''
        if modvals:
            self.modvals(modvals)
        logging.debug("Freeh started")

    def modvals(self, m):
        for key in m:
            if key == 'scale':
                if turbogo_helpers.is_positive_float(m[key]):
                    self.scale = m[key]
                else:
                    raise(FreehError("Bad arg for {}: {}").format(key, m[key]))
            elif key == 'tstart':
                if turbogo_helpers.is_positive_float(m[key]):
                    self.tstart = m[key]
                else:
                    raise(FreehError("Bad arg for {}: {}").format(key, m[key]))
            elif key == 'tend':
                if turbogo_helpers.is_positive_float(m[key]):
                    self.tend = m[key]
                else:
                    raise(FreehError("Bad arg for {}: {}").format(key, m[key]))
            elif key == 'numt':
                if turbogo_helpers.is_positive_int(m[key]):
                    self.numt = m[key]
                else:
                    raise(FreehError("Bad arg for {}: {}").format(key, m[key]))
            elif key == 'pstart':
                if turbogo_helpers.is_positive_float(m[key]):
                    self.pstart = m[key]
                else:
                    raise(FreehError("Bad arg for {}: {}").format(key, m[key]))
            elif key == 'pend':
                if turbogo_helpers.is_positive_float(m[key]):
                    self.pend = m[key]
                else:
                    raise(FreehError("Bad arg for {}: {}").format(key, m[key]))
            elif key == 'nump':
                if turbogo_helpers.is_positive_int(m[key]):
                    self.nump = m[key]
                else:
                    raise(FreehError("Bad arg for {}: {}").format(key, m[key]))
            else:
                raise FreehError(
                    "Invalid arg passed to freeh: {}".format(key))
        if self.tstart:
            self.modvalstring += "tstart={} ".format(self.tstart)
        if self.tend:
            self.modvalstring += "tend={} ".format(self.tend)
        if self.numt:
            self.modvalstring += "numt={} ".format(self.numt)
        if self.pstart:
            self.modvalstring += "pstart={} ".format(self.pstart)
        if self.pend:
            self.modvalstring += "pend={} ".format(self.pend)
        if self.nump:
            self.modvalstring += "nump={} ".format(self.nump)

    def run_freeh(self):
        """
        Runs freeh
        """
        try:
            self.freeh = pexpect.spawn("freeh")
        except Exception as e:
            try:
                self.freeh = pexpect.spawn(os.path.join(TURBOSCRIPT, 'freeh'))
            except Exception as e:
                raise FreehError(
                    "Error starting freeh {}. Check the environment is set up".format(
                    str(e)))
            else:
                logging.debug("Environment not set up. Manually loaded freeh")
        else:
            logging.debug("Freeh instance spawned and active.")

        self.freeh.timeout = self.timeout
        self.fout = file('freeh', 'w')

        out = self.freeh.expect([
            '   ****  freeh : all done  ****',
            'Hit RETURN to accept or enter a different'
        ])
        if out == 0:
            #Not a valid directory to run freeh in
            logging.debug("No vibrational modes found in directory.")
            raise NoVibError("No vibrational modes found in directory.")

        self.freeh.sendline('')
        self.freeh.expect('enter new value for corr, if you want to change')
        if self.scale:
            self.freeh.sendline(self.scale)
        else:
            self.freeh.sendline('')

        #start the logfile now, this should capture freeh data. Calling function
        #either reprocess output or let it remain in directory.
        
        self.freeh.ligfile_read = self.fout
        self.freeh.sendline(self.modvalstring)
        
        self.freeh.expect('or enter  q  or  *  to quit')
        self.freeh.sendline('q')


def proc_freeh(freehfile = ''):
    """Process the freeh output file & return dict of params and data"""
    if not freehfile:
        freehfile = 'freeh'
    fh = turbogo_helpers.read_clean_file('freehfile')
    params = dict()
    data = dict()
    lstart = 0
    for i in range(0, len(fh)):
        if 'your wishes are :' in fh[i]:
            lstart = i
    params['pstart'] = fh[lstart+3].strip().split()[1]
    params['pend'] = fh[lstart+3].strip().split()[3]
    params['nump'] = fh[lstart+3].strip().split()[5]
    params['tstart'] = fh[lstart+5].strip().split()[1]
    params['tend'] = fh[lstart+5].strip().split()[3]
    params['numt'] = fh[lstart+5].strip().split()[5]

    data['zpe'] = fh[lstart+9].strip().split()[1]
    data['t'] = list()
    data['p'] = list()
    data['qtrans'] = list()
    data['qrot'] = list()
    data['qvib'] = list()
    data['pot'] = list()
    data['eng'] = list()
    data['ent'] = list()
    data['cv'] = list()
    data['cp'] = list()

    dataline = lstart + 14
    line = fh[dataline]

    while line.strip() != '':
        data['T'] = line.strip().split()[0]
        data['P'] = line.strip().split()[1]
        data['lnqtrans'] = line.strip().split()[2]
        data['lnqrot'] = line.strip().split()[3]
        data['lnqvib'] = line.strip().split()[4]
        data['chempot'] = line.strip().split()[5]
        data['energy'] = line.strip().split()[6]
        data['entropy'] = line.strip().split()[7]
        dataline += 1
        line = fh[dataline]

    dataline += 3
    line = fh[dataline]
    while line.strip() != '':
        data['cv'] = line.strip().split()[2]
        data['cp'] = line.strip().split()[3]
        dataline += 1
        line = fh[dataline]

    return params, data


if __name__ == "__main__":
    print "Not a callable script. Please run Turbogo or TurboControl."
    exit()
