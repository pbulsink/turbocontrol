#!/usr/bin/env python
"""
Turbocontrol is a controller app for turbogo jobs. Running on one process (or
even on the headnode) it directs turbogo to be run on a series of turbogo
inputs found in sub directories. Monitors for completion of jobs then can auto
prepare for frequency analysis via NumForce or aoforce.
"""

from turbogo import jobrunner, check_input_file, submit_script_prepare
from turbogo import JobLogicError, submit_job
import utilities.turbogo_helpers
import os, sys, shutil
from time import sleep, strftime, time
from datetime import timedelta
import logging
import argparse
from utilities.screwer_op import Screwer
from utilities.freeh_op import Freeh, proc_freeh


try:
    import openbabel
except ImportError:
    reformat = False
else:
    from utilities.formatter import convert_filetype
    reformat = True

TOPDIR = os.path.abspath(os.path.dirname(os.curdir))


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class SetupSubmitError(Error):
    """
    Error in Setup or Submitting a Job

    Attributes:
        expr -- input expression that failed
        msg  -- explanation of error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg


class Jobset():
    """
    Container for information about the job. Including the job object from
    turbogo itself, and other referenced information (directory, input file...)
    """
    def __init__(self, indir, infile, job, freqopt=None, jobid=None,
                 status='Initialized'):
        """Initialization of jobset"""
        self.indir = indir
        self.infile = infile
        self.freqopt = freqopt
        self.status = status
        self.jobid = jobid
        self.job = job
        self.name = os.path.join(self.indir, self.infile)
        self.otime = 0
        self.ftime = 0
        self.curstart = 0
        self.firstfreq = None
        self.ts = False
        self.freeh = False

    def submit(self):
        """
        Submits the job to turbogo for preparation and running, getting
        freqopts, job id and the job object back
        """
        os.chdir(self.indir)
        try:
            self.jobid, freqopt, self.name, self.jobtype = jobrunner(job=self.job)
            if self.jobtype != 'sp':
                self.freqopt = freqopt.split('+')[0]
                if len(freqopt.split('+')) == 2:
                    self.freeh = True
                if self.jobtype == 'opt' or self.jobtype == 'optfreq':
                    self.status = "Opt Submitted"
                elif self.jobtype == 'numforce' or self.jobtype == 'aoforce':
                    self.status = "Freq Submitted"
                elif self.jobtype == 'ts':
                    self.status = 'TS Submitted'
                    self.ts = True
                    if not self.freqopt:
                        self.freqopt = 'numforce'
            elif self.jobtype == 'sp':
                self.status = 'SP Submitted'
        except Exception as e:
            self.jobid = None
            self.job = None
            self.freqopt = None
            self.status = "Submit Failed: {}".format(e)
        os.chdir(TOPDIR)


def find_inputs():
    """
    Finds the inputs in subdirs. Verifies the appropriateness of
    each input file. Returns Dictionary of {dir: inputfile}
    """
    inputdirs = list()
    filetree = dict()

    results = list()
    #find files in dirs:
    for d, _, filenames in os.walk(os.curdir):
        for f in filenames:
            fileExt = os.path.splitext(f)[-1]
            if (fileExt == '.in' or fileExt == '.gjf' or fileExt == '.com'
                or fileExt == '.inp' or fileExt == '.input'):
                results.append(os.path.join(d,f))

    for r in results:
        if os.path.dirname(r) in filetree:
            filetree[os.path.dirname(r)].append(os.path.basename(r))
        else:
            filetree[os.path.dirname(r)] = [os.path.basename(r)]

    multidir = list()
    badinput = list()

    logging.debug("{} potential inputs found".format(len(filetree)))
    inputdirs = dict()
    for key in filetree:
        for v in filetree[key]:
            job = check_input_file(os.path.join(key, v))
            if job:
                if key in inputdirs:
                    logging.warning("More than one valid input file in {}." \
                        "Please have only one input per directory.".format(key))
                    multidir.append(key)
                else:
                    inputdirs[key] = [v, job]
            else:
                logging.warning("File {} not valid input.".format(
                    str(os.path.join(key, v))))
                badinput.append(str(os.path.join(key, v)))
        if key not in inputdirs:
            logging.warning(
                "Directory {} does not contain valid input.".format(key))

    if len(badinput) > 0:
        logging.info("Following inputs have errors:\n{}".format(
            turbogo_helpers.list_str(badinput)))

    if len(multidir) > 0:
        logging.info("Following directories have too many inputs:\n{}".format(
            turbogo_helpers.list_str(multidir)))

    return inputdirs


def check_opt(job):
    """
    Check if an opt job is done or crashed, if done: resubmit to queue if freq
    is required. Return a status string
    """
    if turbogo_helpers.check_files_exist([
        os.path.join(job.indir, 'GEO_OPT_CONVERGED')]):
        #Job converged
        logging.info('Job {} completed optimization.'.format(job.name))
        if job.jobtype == 'opt' or job.jobtype == 'optfreq':
            opttime = turbogo_helpers.get_calc_time(job.indir, 'opt.out')
        elif job.jobtype == 'ts':
            opttime = turbogo_helpers.get_calc_time(job.indir, 'ts.out')
        elif job.jobtype == 'sp':
            opttime = turbogo_helpers.get_calc_time(job.indir, 'sp.out')
        else:
            opttime = False
        if opttime:
            job.otime += opttime
        else:
            job.otime += (time() - job.curstart)

        if job.freqopt != None:
            newid = freq_submit(job)
            if newid != -99:
                job.curstart = time()
                job.jobid = newid
                job.status = "Freq Submitted"
                return 'freq'
            else:
                job.status = "Freq Setup Failed"
                return 'fcrashed'
        else:
            if reformat:
                convert_filetype(os.path.join(job.indir, 'finalgeometry.xyz'),
                                 os.path.join(job.indir, 'finalgeometry.mol'))
            return 'completed'

    else:
        logging.warning("Job {} crashed in optimization."
                     .format(job.name))
        job.status = "Opt Crashed"
        return 'ocrashed'


def check_freq(job):
    """
    Check if a freq job is done or crashed, if done: check for imaginary and
    send for adjustment if required.
    Return a status string
    """

    if job.freqopt == 'numforce':
        filetoread = os.path.join(job.indir, 'numforce', 'aoforce.out')
        endfile = 'numforce.out'
    else:
        filetoread = os.path.join(job.indir, 'aoforce.out')
        endfile = 'aoforce.out'

    try:
        with open(filetoread, 'r') as f:
            endstatus = f.readlines()[-5]
    except (OSError, IOError) as e:
        endstatus = ''
        logging.info(
            "Error {} reading aoforce.out for {}".format(
                e, job.indir))

    else:
        if "   ****  force : all done  ****" in endstatus:

            freqtime = turbogo_helpers.get_calc_time(job.indir, endfile)
            if freqtime:
                job.ftime += freqtime
            else:
                job.ftime += (time() - job.curstart)

            logging.info('Job {} completed frequency.'.format(job.name))
            job.status = "Completed Freq"
            if not job.ts:
                status = ensure_not_ts(job)
            else:
                status = ensure_ts(job)
            if status == 'completed':
                if job.freeh:
                    logging.debug('Do Freeh')
                    do_freeh(job)
                return 'completed'
            elif status == 'error':
                return 'ocrashed'
            elif status == 'opt':
                return 'opt'
            elif status == 'same':
                return 'same'
            elif status == 'imaginary':
                return 'imaginary'
            elif status == 'ts':
                return 'ts'
        else:
            job.status = "Freq Crashed"
            return 'fcrashed'


def ensure_not_ts(job):
    """
    This runs to read out the vibrational modes. If there are negatives, runs
    screwer to adjust the geometry along the imaginary coordinate, and
    resubmits job.
    """
    if job.freqopt == 'numforce':
        newdir = os.path.join(job.indir, 'numforce')
    else:
        newdir = job.indir
    filetoread = os.path.join(newdir, 'control')

    controlfile = turbogo_helpers.read_clean_file(filetoread)

    vib1 = False

    for i in range(len(controlfile)):
        if '$vibrational spectrum' in controlfile[i]:
            for j in range (i+3, len(controlfile)):
                col = controlfile[j][15:34].strip()
                if not (col == '0.00' or col == '-0.00'):
                    try:
                        vib1 = float(col)
                    except ValueError:
                        pass
                    else:
                        mode = controlfile[j][:6].strip()
                        break
        if vib1:
            break

    if vib1:
        if job.firstfreq == vib1:
            #Found the same TS as before. End job.
            return 'same'
        job.firstfreq = vib1
        if vib1 < 0:
            os.chdir(newdir)
            screwer = Screwer(mode)
            try:
                screwer.run_screwer()
            except Exception as e:
                logging.warning("Error '{}' running screwer on job {}.".format(
                    e, job.name))
                os.chdir(TOPDIR)
                return "error"
            control = turbogo_helpers.read_clean_file('control')
            newcoord = list()
            readin = False
            for line in control:
                if '$newcoord' in line:
                    readin = -1
                elif '$end' in line:
                    readin = False
                if readin:
                    newcoord.append(line)
                elif readin == -1:
                    readin = True
            if job.freqopt == 'numforce':
                os.chdir(os.pardir)
                turbogo_helpers.write_file('coord', newcoord)
                try:  # Better to remove numforce, if not no biggie
                    os.remove(os.path.join(os.curdir, 'control'))
                    shutil.rmtree(os.path.join(os.curdir, 'numforce'))
                except OSError:
                    pass
            try:
                job.jobid, job.freqopt, job.name, job.jobtype = jobrunner(job=self.job)
                job.curstart = time()
            except Exception as e:
                logging.warning("Error {} resubmitting job {}.".format(
                    e, job.name))
                os.chdir(TOPDIR)
                return 'error'
            os.chdir(TOPDIR)
            return 'opt'
        else:
            return 'completed'
    else:
        logging.warning(
            'Error getting vibrational frequencies from job {}.'.format(
            job.name
        ))
        return 'error'


def ensure_ts(job):
    """
    This runs to read out the vibrational modes. If there are more than one negative,
    run screwer to adjust the geometry along the imaginary coordinate, and
    resubmits job.
    """
    if job.freqopt == 'numforce':
        newdir = os.path.join(job.indir, 'numforce')
    else:
        newdir = job.indir
    filetoread = os.path.join(newdir, 'control')

    controlfile = turbogo_helpers.read_clean_file(filetoread)

    vib1= False
    vib2 = False

    for i in range(len(controlfile)):
        if '$vibrational spectrum' in controlfile[i]:
            for j in range (i+3, len(controlfile)):
                col = controlfile[j][15:34].strip()
                if col != '0.00':
                    try:
                        if not vib1:
                            vib1 = float(col)
                        elif not vib2:
                            vib2 = float(col)
                    except ValueError:
                        pass
                    else:
                        mode = controlfile[j][:6].strip()
        if vib2:
            break

    if vib1 and vib2:
        if vib1 < 0 and vib2 > 0:
            return 'ts'
        elif vib1 > 0:
            return 'opt'
        elif vib2 < 0:
            return 'imaginary'  # itvc = 1 SHOULD only ever return 1 img. freq
    else:
        logging.warning(
            'Error getting vibrational frequencies from job {}.'.format(
            job.name
        ))
        return 'error'


def do_freeh(job):
    """
    Does freeh analysis on job if requested
    """

    if job.freqopt == 'numforce':
        newdir = os.path.join(job.indir, 'numforce')
    else:
        newdir = job.indir

    os.chdir(newdir)
    freeh = Freeh()
    logging.debug('doing freeh')
    try:
        freeh.run_freeh()
    except Exception as e:
        logging.warn('freeh failed with exception {}'.format(e))
    else:
        logging.debug('freeh completed')
        job.params, job.data = proc_freeh()

    os.chdir(TOPDIR)

    if job.params:
        write_freeh(job)
        logging.debug('freeh written')
    

def write_stats(job):
    """
    Writes a line to the stats file for each job that completes successfully.
    """
    if not turbogo_helpers.check_files_exist(['stats.txt']):
        #write the header to the file
        try:
            with open('stats.txt', 'w') as f:
                f.write("{name:^16}{directory:^20}{optsteps:^10}{opttime:^12}" \
                        "{freqtime:^12}{tottime:^12}{firstfreq:^16}{energy:^16}"
                .format(
                    name='Name',
                    directory = 'Directory',
                    optsteps = 'Opt Steps',
                    opttime = 'Opt Time',
                    freqtime = 'Freq Time',
                    tottime = 'Total Time',
                    firstfreq = '1st Frequency',
                    energy = 'Energy',
                ))
                f.write('\n')
        except IOError as e:
            logging.warning("Error preparing stats file: {}".format(e))
        except Exception as e:
            logging.warning("Unknown error {}".format(e))
    name = job.name
    directory = os.path.join(job.indir, job.infile)
    try:
        with open(os.path.join(job.indir, 'energy')) as f:
            lines = f.readlines()
    except IOError as e:
        logging.warning("Error reading energy file for stats: {}".format(e))
        optsteps = '?'
        energy = '?'
    except Exception as e:
        logging.warning("Unknown error {}.".format(e))
    else:
        optsteps = lines[-2][:6].strip()
        energy = lines[-2][6:22].strip()
    opttime = turbogo_helpers.time_readable(job.otime)
    freqtime = turbogo_helpers.time_readable(job.ftime)
    tottime = turbogo_helpers.time_readable(job.otime + job.ftime)
    firstfreq = job.firstfreq
    try:
        with open('stats.txt', 'a') as f:
            f.write("{name:^16.16}{directory:^20.20}{optsteps:^10.10}" \
                    "{opttime:^12.12}{freqtime:^12.12}{tottime:^12.12}" \
                    "{firstfreq:^16.16}{energy:^16.16}"
            .format(
                name=name,
                directory = directory,
                optsteps = optsteps,
                opttime = opttime,
                freqtime = freqtime,
                tottime = tottime,
                firstfreq = firstfreq,
                energy = energy,
            ))
            f.write('\n')
    except (OSError, IOError) as e:
        logging.warning("Error writing stats file: {}".format(e))


def write_freeh(job):
    """
    Writes a line to the freeh file for each job that completes successfully
    with freeh requested.
    """
    if not turbogo_helpers.check_files_exist(['freeh.txt']):
        #write the header to the file
        try:
            with open('freeh.txt', 'w') as f:
                f.write("{name:^16}{directory:^20}{zpe:^14}{t:^10}" \
                        "{p:^11}{qtrans:^12}{qrot:^10}" \
                        "{pot:^14}{eng:^14}{entr:^20}{cv:^14}{cp:^14}{enth:^14}\n"
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
                logging.debug("Wrote freeh titles")
        except IOError as e:
            logging.warning("Error preparing freeh file: {}".format(e))
        except Exception as e:
            logging.warning("Unknown error {}".format(e))
    name = job.name
    directory = os.path.join(job.indir, job.infile)
    zpe = job.data['zpe']
    t = job.data['t']
    p = job.data['p']
    qtrans = job.data['qtrans']
    qrot = job.data['qrot']
    qvib = job.data['qvib']
    pot = job.data['pot']
    eng = job.data['eng']
    entr = job.data['entr']
    cv = job.data['cv']
    cp = job.data['cp']
    enth = job.data['enth']
    
    try:
        with open('freeh.txt', 'a') as f:
            f.write("{name:^16}{directory:^20}{zpe:^14}{t:^10}" \
                    "{p:^11}{qtrans:^12}{qrot:^10}" \
                    "{pot:^14}{eng:^14}{entr:^20}{cv:^14}{cp:^14}{enth:^14}\n"
            .format(
                name=name,
                directory = directory,
                zpe = zpe,
                t = t[0],
                p = p[0],
                qtrans = qtrans[0],
                qrot = qrot[0],
                qvib = qvib[0],
                pot = pot[0],
                eng = eng[0],
                entr = entr[0],
                cv = cv[0],
                cp = cp[0],
                enth = enth[0]
            ))
            if len(t) > 1: #don't rewrite name/zpe for each line
                for i in range(1, len(t)):
                    f.write("{name:^16}{directory:^20}{zpe:^14}{t:^8}" \
                    "{p:^11}{qtrans:^12}{qrot:^10}" \
                    "{pot:^14}{eng:^14}{entr:^20}{cv:^14}{cp:^14}{enth:^14}\n"
                .format(
                    name='',
                    directory = '',
                    zpe = '',
                    t = t[i],
                    p = p[i],
                    qtrans = qtrans[i],
                    qrot = qrot[i],
                    qvib = qvib[i],
                    pot = pot[i],
                    eng = eng[i],
                    entr = entr[i],
                    cv = cv[i],
                    cp = cp[i],
                    enth = enth[i]
                ))
    except (OSError, IOError) as e:
        logging.warning("Error writing freeh file: {}".format(e))


def watch_jobs(jobs):
    """
    Monitors jobs running. If jobs request frequency, then submits to frequency
    calculation
    """
    orunning = list()
    frunning = list()
    ocomplete = list()
    fcomplete = list()
    ocrashed = list()
    fcrashed = list()
    crashed = list()
    completed = list()
    failed_submit = list()
    stuck = list()

    allcomplete = False
    jobdict = dict()

    starttime = time()

    for job in jobs:
        if job.status == 'Opt Submitted' or job.status == 'TS Submitted':
            orunning.append(job.jobid)
            jobdict[job.jobid] = job
        elif job.status == 'Freq Submitted':
            frunning.append(job.jobid)
            jobdict[job.jobid] = job
        else:
            failed_submit.append(job.name + ' - ' + job.status)
        

    logging.info('There are {} jobs being watched.'.format(
        len(jobdict)
        ))

    if len(failed_submit) > 0:
        logging.warning('There are {} jobs that failed to launch:\n{}'.format(
            len(failed_submit),
            turbogo_helpers.list_str(failed_submit)
            ))
    if len(jobdict) == 0:
        exit()

    loopcount = 0
    change = False
    #delay to ensures all jobs are in queue, and catch first moment fails
    sleep(60)

    while not allcomplete:
        alljobs = turbogo_helpers.get_all_active_jobs()
        if len(alljobs) == 0 and (len(orunning) > 0 or len(frunning) > 0):
            #possible fail at getting jobs from queue
            sleep(60)
            alljobs = turbogo_helpers.get_all_active_jobs()
            if len(alljobs) == 0:
                #One more try
                sleep(300)
                alljobs = turbogo_helpers.get_all_active_jobs()

        checkojobs = list(orunning)
        checkfjobs = list(frunning)

        for job in alljobs:
            if job in checkojobs:
                checkojobs.remove(job)
            elif job in checkfjobs:
                checkfjobs.remove(job)

        if len(checkojobs) != 0:
            #Some jobs not running
            for ojob in checkojobs:
                job = jobdict[ojob]
                del jobdict[ojob]
                orunning.remove(job.jobid)
                #find out what happened to the job & deal with it
                status = check_opt(job)
                if status == 'freq':
                    ocomplete.append(job.name)
                    frunning.append(job.jobid)
                    jobdict[job.jobid] = job
                    logging.debug(
                        "Job {} submitted for freq with jobid {}.".format(
                        job.name, job.jobid
                    ))
                elif status == 'fcrashed':
                    fcrashed.append(job.name)
                    crashed.append(job.name)
                    logging.debug("Job {} crashed starting freq.".format(
                        job.name
                    ))
                elif status == 'ocrashed':
                    ocrashed.append(job.name)
                    crashed.append(job.name)
                    logging.debug("Job {} crashed in opt.".format(
                        job.name
                    ))
                else:
                    completed.append(job.name)
                    write_stats(job)
                    logging.debug("Job {} completed opt.".format(
                        job.name
                    ))
            change = True

        if len(checkfjobs) != 0:
            #some freq not running
            for fjob in checkfjobs:
                job = jobdict[fjob]
                del jobdict[fjob]
                frunning.remove(job.jobid)
                #find out what happened to the job and deal with it
                status = check_freq(job)
                if status == 'opt':
                    #job was resubmitted with new geometry to avoid saddle point
                    orunning.append(job.jobid)
                    jobdict[job.jobid] = job
                    logging.debug(
                        "Job {} resubmitted for opt with jobid {}.".format(
                        job.name, job.jobid
                    ))
                elif status == 'fcrashed':
                    fcrashed.append(job.name)
                    crashed.append(job.name)
                    logging.debug("Job {} crashed starting freq.".format(
                        job.name
                    ))
                elif status == 'ocrashed':
                    ocrashed.append(job.name)
                    crashed.append(job.name)
                    logging.debug("Job {} crashed restarting opt.".format(
                        job.name
                    ))
                elif status == 'same' or status == 'imaginary':
                    stuck.append(job.name)
                    write_stats(job)
                    logging.info(
                        "Job {} stuck on transition state with freq {}.".format(
                            job.name, job.firstfreq))
                elif status == 'ts':
                    write_stats(job)
                    completed.append(job.name)
                    logging.debug("Job {} completed ts.".format(
                        job.name
                    ))
                else:
                    write_stats(job)
                    completed.append(job.name)
                    logging.debug("Job {} completed freq.".format(
                        job.name
                    ))
            change = True

        if len(orunning) == 0 and len(frunning) == 0:
            #all jobs finished or crashed:
            allcomplete = True
        else:
            if loopcount % (3*6) == 0 and change == True:
                #3-Hourly status update if a change happened
                logstring = "\n----------------------------------------------" \
                            "------\n"
                logstring += "At {}:\n".format(strftime("%d/%m/%y %H:%M:%S"))
                if len(orunning) > 0:
                    logstring += "There are {} running opt jobs:\n{}\n".format(
                        len(orunning), turbogo_helpers.list_str(orunning))
                if len(frunning) > 0:
                    logstring += "There are {} running freq jobs:\n{}\n".format(
                        len(frunning), turbogo_helpers.list_str(frunning))
                if len(crashed) > 0:
                    logstring += "There are {} crashed jobs:\n{}\n".format(
                        len(crashed),
                        turbogo_helpers.list_str(crashed))
                if len(stuck) > 0:
                    logstring += "There are {} stuck jobs:\n{}\n".format(
                        len(stuck), turbogo_helpers.list_str(stuck))
                if len(completed) > 0:
                    logstring += "There are {} completed jobs:\n{}\n".format(
                        len(completed), turbogo_helpers.list_str(completed))
                logstring += "-----------------------------------------------" \
                             "-----"
                logging.info(logstring)
                change = False
            loopcount += 1
            sleep(10*60)

    #after job finished/crashed logging
    elapsed = turbogo_helpers.time_readable(time()-starttime)

    logging.warning("{} jobs completed. {} jobs crashed.".format(
        len(fcomplete),len(crashed)))

    logstring = "\n----------------------------------------------------\n"
    logstring += "Completed at {} after {}:\n".format(
        strftime("%d/%m/%y %H:%M:%S"), elapsed)
    if len(completed) > 0:
        logstring += "There are {} completed jobs:\n{}\n".format(
            len(completed), turbogo_helpers.list_str(completed))
    if len(stuck) > 0:
        logstring += "There are {} stuck jobs:\n{}\n".format(
            len(stuck), turbogo_helpers.list_str(stuck))
    if len(crashed) > 0:
        logstring += "There are {} crashed jobs:\n{}\n".format(
            len(crashed), turbogo_helpers.list_str(crashed))
    if len(failed_submit) > 0:
        logstring += "There are {} jobs that failed to start:\n{}\n".format(
            len(failed_submit), turbogo_helpers.list_str(failed_submit))
    logstring += "----------------------------------------------------"
    logging.info(logstring)


def freq_submit(job):
    """
    Sends job for frequency analysis of type 'job.freqtype'
    """
    os.chdir(job.indir)
    if job.freqopt == 'aoforce':
        try:
            turbogo_helpers.add_or_modify_control(['$les all 2', '$maxcor 2056'])
        except turbogo_helpers.ControlFileError:
            logging.warn("Error modifying control file. Attempting to continue.")
    job.job.jobtype = job.freqopt
    script = submit_script_prepare(job.job)
    try:
        jobid = submit_job(job.job, script)
    except Exception as e:
        logging.warning("Error {} submiting freq job {}".format(e, job.indir))
        return -99
    logging.info("Job {} submitted for {} analysis"
                 .format(job.name, job.freqopt))
    os.chdir(TOPDIR)
    return jobid


def main():
    """First call on the code"""
    logging.basicConfig(
        format=('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'),
        filename='turbocontrol.log',
        level=logging.DEBUG)
    logging.info('Started')
    p = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(prog="TurboControl",
                                     description="Usage: %prog [options]")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true',
                        help='Run more verbose (show debugging info)')
    group.add_argument('-q', '--quiet', action="store_true",
                        help='Run less verbose (show only warnings)')
    parser.add_argument('-s', '--solvent', dest="solvent", action="store_true",
                        help='Show solvents known to Turbocontrol')
    args = parser.parse_args()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    if args.solvent:
        print "\n".join(sorted(turbogo_helpers.DIELECTRICS.keys(), key=lambda s: s.lower()))
        exit()
    if args.verbose:
        ch.setLevel(logging.DEBUG)
    elif args.quiet:
        ch.setLevel(logging.WARNING)
        logging.getLogger().setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
        )
    ch.setFormatter(formatter)

    logging.getLogger().addHandler(ch)

    start = time()

    inputdirs = find_inputs()
    inputfiles = list()
    for key in inputdirs:
        inputfiles.append(str(os.path.join(key, inputdirs[key][0])))

    logging.info("Inputs found at:\n{}".format(
        turbogo_helpers.list_str(sorted(inputfiles))))

    jobs = list()
    for key in inputdirs:
        job = Jobset(key, inputdirs[key][0], inputdirs[key][1])
        job.submit()
        job.curstart = time()
        if not args.verbose:
            try:
                os.remove(os.path.join(key, 'define.log'))
            except (OSError, IOError):
                pass
        jobs.append(job)
    end = time() - start
    logging.info("Set up and submitted {} jobs in {} seconds.".format(
        len(jobs),end))

    if len(jobs) > 0:
        watch_jobs(jobs)
    else:
        logging.warning("No jobs submitted. Exiting.")

    exit()


if __name__ == '__main__':
    main()
