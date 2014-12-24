#!/usr/bin/env python
"""
Simple operating code for Turbomole
Reads input, sets up job via define, generates the submit script
depending on number of cores requested, and submits.
Future watch jobs & do sequential calculations (ie opt then freq).
Input files are formatted as gaussian, with additional/alternative keywords.
"""

import argparse
import time
import logging
import sys
from subprocess import Popen, PIPE

import src.def_op
import src.cosmo_op
import src.turbogo_helpers
import os

DEFAULT_FREQ = 'numforce'


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputSyntaxError(Error):
    """
    Error in input file due to syntax

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg


class SubmitScriptError(Error):
    """
    Submit Script generation and writing errors
    Attributes:
        msg - cause of error
        e - exception
    """
    def __init__(self, msg, e):
        self.msg = msg
        self.e = e


class CoordError(Error):
    """
    Coord generation and writing errors
    Attributes:
        msg - cause of error
        e - exception
    """
    def __init__(self, msg, e):
        self.msg = msg
        self.e = e


class JobLogicError(Error):
    """
    Job Logic Error (aoforce before optimization, etc)
    Attributes:
        msg - cause of error
    """
    def __init__(self, msg):
        self.msg = msg


class Job():
    """Job Class to store variables"""

    def __init__(self, name='', basis='def2-tzvp', functional='tpss',
                 jobtype='opt', spin=1, iterations=300, charge=0, ri=None,
                 marij=None, disp=None, para_arch='GA', nproc=1,
                 freqopts=None, freeh=None, rt=168, cosmo=None, data=None,
                 params=None, indir=None, infile=None):
        #data doesn't need to be validated, it is when read from inputfile
        self.name = name
        self.basis = basis
        self.functional = functional
        self.jobtype = jobtype
        if jobtype == 'ts':
            self.ts = True
        else:
            self.ts = False
        self.iterations = iterations
        self.charge = charge
        self.spin = spin
        self.ri = ri
        self.marij = marij
        if functional == 'b97-d':
            self.disp = True
        else:
            self.disp = disp
        self.freeh = freeh
        self.nproc = nproc
        if jobtype == 'freq' or jobtype == 'aoforce':
            self.para_arch = 'SMP'
        else:
            self.para_arch = para_arch
        self.control_add = list()
        self.control_remove = list()
        self.geometry = list()
        self.freqopts = freqopts
        self.rt = "{}:00:00".format(rt)
        self.cosmo = cosmo
        self.data = data
        self.params = params
        self.indir = indir
        self.infile = infile
        self.otime = 0
        self.ftime = 0

def jobsetup(infile):
    """
    Read the input file, get the keyword flags & geometry. Utilizes a gaussian
    type input file.
    """

    lines = turbogo_helpers.read_clean_file(infile)

    iargs = list()
    igeom = list()
    control_add = list()
    control_remove = list()

    #first parse %args from top of file
    lines.reverse()
    moreargs = True
    while moreargs:
        if lines[-1][0] == '%':
            iargs.append(lines.pop())
        else:
            moreargs = False

    args = turbogo_helpers.check_args(iargs)
    logging.debug("{} args processed".format(len(args)))

    #immediately following %args is the #route card
    if not lines[-1][0] == '#':
        logging.error("""Syntax error at route. Must immediately follow
                      arguements ('%') and start with #""")
        raise InputSyntaxError(str(lines[0]), """Syntax error at route.
                               Must immediately follow arguements ('%') and
                               start with #""")
    else:
        iroute = lines.pop()

    logging.debug("Parsing input route card.")
    route = turbogo_helpers.check_route(iroute)
    logging.debug("{} Route parameters processed".format(len(route)))

    #specs from gaussian: blank line required
    if not lines[-1] == '':
        logging.error("""Syntax error after route. Blank line required before
                      title""")
        raise InputSyntaxError(str(lines[0]), """Syntax error after route.
                               Blank line required before title""")
    else:
        del lines[-1]

    #Now is the job title.
    title = str(lines[-1])
    logging.debug("Title: {}".format(title))
    del lines[-1]

    #Gaussian spec another blank line
    if not lines[-1] == '':
        logging.error("""Syntax error after title. Blank line required before
                      charge & spin""")
        raise InputSyntaxError(str(lines[0]), """Syntax error after title.
                               Blank line required before charge & spin""")
    else:
        del lines[-1]

    #Charge and spin (0 1)
    ichspin = lines[-1]
    ch_spin = turbogo_helpers.check_chspin(ichspin)
    logging.debug("Charge of {} and spin of {}.".format(ch_spin['ch'],
                                                   ch_spin['spin']))
    del lines[-1]

    #Input Geometry in xyz cartesian format
    moregeom = True
    while moregeom:
        if not lines[-1][:1] == '':
            igeom.append(lines.pop())
        else:
            moregeom = False

    geom = turbogo_helpers.check_geom(igeom)
    logging.debug("{} lines of geometry processed".format(len(geom)))

    #gaussian spec blankline
    if not lines[-1] == '':
        logging.error("Syntax error after geometry. Blank line required.")
        raise InputSyntaxError(str(lines[0]), """Syntax error after geometry.
                               Blank line required.""")
    else:
        del lines[-1]

    #new spec: manual add or subtract from control file with:
    #$opt to add, or:
    #-$opt to remove
    if len(lines) > 0:
        logging.debug("Parsing additional control arguements")
        morelines = True
        while morelines:
            try:
                if lines[-1][0] == '$' or lines[-1][0] == '-' and lines[-1][1] == '$':
                    if lines[-1][0] == '$':
                        control_add.append(lines.pop())
                    else:
                        control_remove.append(lines.pop())
                else:
                    morelines = False
            except IndexError:
                morelines = False
        logging.debug("{} additional lines processed".format(len(control_add)))

    #Set up job.class
    logging.debug("Setting up Job with collected information.")
    job = Job()
    job.name = title
    job.charge = ch_spin['ch']
    job.spin = ch_spin['spin']
    if 'basis' in route:
        job.basis = route['basis']
    if 'functional' in route:
        job.functional = route['functional']
    if 'jobtype' in route:
        job.jobtype = route['jobtype']
    else:
        job.jobtype = 'sp'
    if job.jobtype == 'opt' or job.jobtype == 'optfreq':
        #one atom checking - can't opt one atom, so single point it.
        if len(geom) == 1:
            logging.debug('One atom job changed to SP')
            job.jobtype = 'sp'
    if 'freqopts' in route and job.jobtype != 'sp':
        job.freqopts = route['freqopts']
    elif job.jobtype == 'freq' and not 'freqopts' in route:
        job.freqopts = DEFAULT_FREQ
    elif job.jobtype == 'ts' and not 'freqopts' in route:
        job.freqopts = DEFAULT_FREQ
    if 'ri' in route:
        job.ri = True
    else:
        job.ri = False
    if 'marij' in route and 'ri' in route:
        job.marij = True
    else:
        job.ri = False
    if 'disp' in route or job.functional == 'b97-d':
        job.disp = True
    if 'freeh' in route:
        job.freeh = True
    if job.freeh:
        job.freqopts += '+freeh'
    if 'iterations' in args:
        job.iterations = int(args['iterations'])
    elif 'maxcycles' in args:
        job.iterations = int(args['maxcycles'])
    if 'nproc' in args:
        job.nproc = int(args['nproc'])
    if 'cosmo' in args:
        job.cosmo = args['cosmo']
    if 'rt' in args:
        job.rt = "{}:00:00".format(args['rt'])
    if job.jobtype != 'freq':
        if 'arch' in args:
            job.para_arch = args['arch']
    else:
        job.para_arch = 'SMP'
    if 'mod' in args and not args['mod']:
        logging.debug("No mod of control requested")
    else:
        control_add = turbogo_helpers.auto_control_mod(control_add, job)
    job.control_add = control_add
    job.control_remove = control_remove
    job.geometry = geom
    return job


def write_coord(job, filename='coord'):
    """Write the coord file"""
    job.geometry.insert(0, '$coord')
    job.geometry.append('$end')
    turbogo_helpers.write_file(filename, job.geometry)
    logging.debug('File {} written.'.format(filename))


def run_define(job):
    """Setup and Run Define"""
    define = def_op.Define()
    define.setup_define(job)
    define.start_define()
    exitcode = define.run_define()
    
def run_cosmo(job):
    """Set up and run CosmoPrep"""
    cosmo = cosmo_op.Cosmo()
    cosmo.setup_cosmo(job)
    cosmo.start_cosmo()
    exitcode = cosmo.run_cosmo()


def control_edit(job, filename='control'):
    """Edit the control files to include or remove the required lines"""
    logging.debug("Editing control file to add additional info.")
    turbogo_helpers.remove_control(job.control_remove, filename)
    turbogo_helpers.add_or_modify_control(job.control_add, filename)


def submit_script_prepare(job, filename='submitscript.sge'):
    """Write a submit script for gridengine for the job."""

    logging.debug("Preparing gridengine submit script")

    #NPROC has to be one less for MPI jobs
    nproc = job.nproc
    if job.para_arch == "MPI":
        nproc = nproc - 1

    env_mod = ''
    #env = turbogo_helpers.check_env()
    #if env:
    #    logging.warn("Env vars not set. Attempting to fix via submit script")
    #    for key in env:
    #        env_mod += "export {}={}\n".format(key, env[key]) 

    #Set up the parallel preamble. No parallel arch info if numforce
    if job.jobtype != 'numforce':
        preamble_template = """export PARA_ARCH={para_arch}\n""".format(
            para_arch = job.para_arch)
    else:
        preamble_template=''

    preamble_template += """export MPI_IC_ORDER="TCP"
export PARNODES={nproc}
cat $PE_HOSTFILE | awk '{{for(i=0;i<$2;i++) print $1}}' > hosts_file
export HOSTS_FILE=`readlink -f hosts_file`
""".format(nproc = nproc)

    if job.nproc > 1:
        parallel_preamble = preamble_template
    else:
        parallel_preamble = ''

    #set up the job command call itself
    if job.jobtype == 'opt' or job.jobtype == 'optfreq':
        jobcommand = 'jobex'
        jobcommand += ' -c {}'.format(job.iterations)
        if job.ri:
            jobcommand += ' -ri'
        #add making xyz sp geom and opt trajectory xyz files after jobex
        jobcommand += ' > opt.out'
        jobcommand += '\nt2x > optimization.xyz\nt2x -c > final_geometry.xyz'

    elif job.jobtype == 'aoforce':
        jobcommand = 'aoforce'
        jobcommand += ' > aoforce.out'

    elif job.jobtype == 'numforce':
        jobcommand = 'NumForce -central'
        if job.ri:
            jobcommand += ' -ri'
        if job.nproc > 1:
            jobcommand += ' -mfile hosts_file'
        jobcommand += ' > numforce.out'

    elif job.jobtype == 'sp':
        if job.ri:
            jobcommand = 'ridft'
        else:
            jobcommand = 'dscf'
        jobcommand += ' > sp.out'

    elif job.jobtype == 'ts':
        if job.ri:
            jobcommand = 'ridft\nrdgrad\njobex -trans -ri'
        else:
            jobcommand = 'dscf\ngrad\njobex -trans'
        if job.iterations:
            jobcommand += ' -c {}'.format(job.iterations)
        jobcommand += ' > ts.out'
        jobcommand += '\nt2x > optimization.xyz\nt2x -c > final_geometry.xyz'

    logging.debug('Job submit script: {} completed.'.format(
        jobcommand.replace('\n', ' & ')))

    #make one big sumbit script
    #runs the jobcommand
    submit_script = """#!/bin/bash
#$ -cwd
#$ -V
#$ -j y
#$ -o {jobname}.stdout
#$ -N tm.{jobname}
#$ -l h_rt={rt}
#$ -R y
#$ -pe threaded {nproc}
{env_mod}
{parallel_preamble}
source $TURBODIR/Config_turbo_env

ulimit -s unlimited

touch startfile

{jobcommand}
""".format(
            jobname=turbogo_helpers.slug(job.name),
            nproc=job.nproc,
            parallel_preamble=parallel_preamble,
            jobcommand=jobcommand,
            env_mod=env_mod,
            rt = job.rt
        )

    #listify script by lines and write lines to file
    try:
        turbogo_helpers.write_file(filename, submit_script.split('\n'))
    except turbogo_helpers.FileAccessError:
        logging.warning("Error writing submit script to file.")
    logging.debug('Submit script generated at {}.'.format(filename))
    return submit_script


def submit_job(job, script=None):
    """Submit the specified job to queue for calculation"""

    logging.debug("Submitting job to queue")

    if not script:
        try:
            script = turbogo_helpers.read_clean_file('submitscript.sge')
        except turbogo_helpers.FileAccessError:
            raise turbogo_helpers.FileAccessError
    #submit job in Popen pipe and get job number back.
    p = Popen('qsub', stdin=PIPE, stdout=PIPE)
    poutput, perr = p.communicate(input=script)
    if 'has been submitted' in poutput:
        jobid = poutput.split('\n')[0].split(' ')[2]
        if turbogo_helpers.is_int(jobid):
            job.jobid = jobid
            logging.info('Job {} with job id {} submitted'.format(
                job.name, jobid))
            turbogo_helpers.write_file('jobid', ["{}: {}".format(job.jobtype, jobid)])
        else:
            job.jobid = None
            logging.warning('Job id unknown.')
    else:
        job.jobid = None
        logging.warning('Error starting job. qsub output: \n{}'.format(poutput))
    return job.jobid


def check_input_file(infile):
    """Checks to see if input file is of valid format. Returns true or false"""
    try:
        return jobsetup(infile)
    except Exception as e:
        logging.warning(
            "Input file '{}' is not valid. Error {}".format(infile, e))
        return False


def jobrunner(infile = None, job = None):
    """
    run the job prep and submit from a specific file or supplied prepared job
    """
    starttime = time.time()
    if not job:
        if infile:
            job = jobsetup(infile)
            logging.debug('Job setup complete.')
        else:
            logging.critical('Job input file or prepared job must be supplied.')
            raise JobLogicError(
                "No input file or supplied prepared job to submit.")
    logging.debug('Working with {}.'.format(job.name))
    write_coord(job)
    logging.debug('coord written')
    if job.jobtype == 'opt' or job.jobtype == 'optfreq' or job.jobtype == 'ts' or job.jobtype == 'sp' or job.jobtype == 'prep':
        defstart = time.time()
        run_define(job)
        logging.debug('define complete.')
        defend = time.time()
        logging.debug("define ended in {0:.2f}s".format(defend-defstart))
    if job.cosmo != None:
        try:
            run_cosmo(job)
        except Exception as e:
            logging.warn("Some error in cosmo running: {}".format(e))
    elif job.jobtype == 'aoforce' or job.jobtype == 'numforce':
        if not turbogo_helpers.check_files_exist(['GEO_OPT_CONVERGED',
                                                  'converged']):
            logging.warning(
                "Convergence required before {} job.".format(job.jobtype)
                )
            raise JobLogicError("Convergence required before {} job.".format(
                job.jobtype))
    if job.control_remove or job.control_add:
        control_edit(job)
        logging.debug('control file editing complete.')
    else:
        logging.debug('No control file edits')
    script = submit_script_prepare(job)
    logging.debug('Submit script written.')
    if job.jobtype != 'prep':
        jobid = submit_job(job, script)
    else:
        logging.info('Job not submitted - prep flag in input.')
    logging.debug("Submitted in {0:.2f} seconds.".format(time.time() - starttime))
    return jobid, job.freqopts, job.name, job.jobtype

def main():
    """Manages the code"""
    logging.basicConfig(
        format=('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'),
        filename='turbogo.log',
        level=logging.DEBUG)
    logging.info('Started')
    parser = argparse.ArgumentParser("Usage: %prog [options]")
    parser.add_argument('file',
                        help="Read input from gaussian-type input FILE")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true',
                        help='Run more verbose (show debugging info)')
    group.add_argument('-q', '--quiet', action="store_true",
                        help='Run less verbose (show only warnings)')
    args = parser.parse_args()

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    if args.verbose:
        ch.setLevel(logging.DEBUG)
    elif args.quiet:
        ch.setLevel(logging.WARNING)
        logging.getLogger().setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
    ch.setFormatter(formatter)
    logging.getLogger().addHandler(ch)
    infile = args.file
    logging.debug("Specified file {} in args".format(infile))

    #check file exists, if not request file.
    ifile = turbogo_helpers.check_files_exist([infile])
    if not ifile:
        logging.critical('Input file {} does not exist.'.format(infile))
        exit()
    #file is good. let's go!
    jobid, freqopts, _name, _type = jobrunner(infile = infile)
    if not args.verbose:
        try:
            os.remove(os.path.join(os.path.curdir, 'define.log'))
        except (OSError, IOError):
            pass
    logging.debug('Jobid: {}\nFreqStatus: {}'.format(jobid, freqopts))
    exit()

if __name__ == "__main__":
    main()
