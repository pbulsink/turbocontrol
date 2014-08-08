#!/usr/bin/env python
"""
Helper functions for the turbogo program. Can be called outside of turbogo.py
with proper args provided.
"""
import logging
import re
import unicodedata
import os
import sys
import time
from subprocess import Popen, PIPE


"""
-------------------------------------------------------------------------------
Change these to reflect your system.
Turbodir is the parent dir for turbomole.
Turbosys is the system name (should be one listed in turbomole/bin)
-------------------------------------------------------------------------------
"""
MAN_TURBODIR = '/share/apps/turbomole/6.5'
MAN_TURBOSYS = 'em64t-unknown-linux-gnu'

"""
-------------------------------------------------------------------------------
"""


ELEMENTS = ['Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'B', 'Ba', 'Be',
            'Bh', 'Bi', 'Bk', 'Br', 'C', 'Ca', 'Cd', 'Ce', 'Cf', 'Cl', 'Cm',
            'Cn', 'Co', 'Cr', 'Cs', 'Cu', 'Db', 'Ds', 'Dy', 'Er', 'Es', 'Eu',
            'F', 'Fe', 'Fl', 'Fm', 'Fr', 'Ga', 'Gd', 'Ge', 'H', 'He', 'Hf',
            'Hg', 'Ho', 'Hs', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lr',
            'Lu', 'Lv', 'Md', 'Mg', 'Mn', 'Mo', 'Mt', 'N', 'Na', 'Nb', 'Nd',
            'Ne', 'Ni', 'No', 'Np', 'O', 'Os', 'P', 'Pa', 'Pb', 'Pd', 'Pm',
            'Po', 'Pr', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rf', 'Rg', 'Rh', 'Rn',
            'Ru', 'S', 'Sb', 'Sc', 'Se', 'Sg', 'Si', 'Sm', 'Sn', 'Sr', 'Ta',
            'Tb', 'Tc', 'Te', 'Th', 'Ti', 'Tl', 'Tm', 'U', 'Uuo', 'Uup', 'Uus',
            'Uut', 'V', 'W', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']

ARGLIST = ['nproc', 'nprocessors', 'nprocshared', 'arch', 'architecture',
           'para_arch', 'maxcycles', 'nocontrolmod', 'autocontrolmod', 'rt',
           'cosmo']
DISCARDARGLIST = ['nosave', 'rwf', 'chk', 'mem']
ROUTELIST = ['opt', 'freq', 'ts', 'td', 'prep', 'sp']
FREQOPTS = ['aoforce', 'numforce']
ROUTEOPTS = ['ri', 'marij', 'disp', 'disp3', 'tight', 'loose', 'freeh']
DISCARDROUTEOPTS = ['guess=indo', 'newestmfc', 'gfinput', 'pop=full', 'hf',
                    'geom=connectivity']
FUNCTIONALS = ['b3lyp', 'b3-lyp', 'blyp', 'b-lyp', 'pbe', 'b97d', 'b97-d',
               'tpss', 'pbe0', 'tpssh', 'bp', 'b-p', 'lhf', 's-vwn', 'svwn',
               'vwn']
PARA_ARCH = ['MPI', 'GA', 'SMP']
BASIS = ['SV', 'SVP', 'SV(P)', 'def-SVP', 'def2-SVP', 'def-SV(P)', 'def2-SV(P)',
         'DZ', 'DZP', 'TZ', 'TZP', 'TZV', 'TZVP', 'def-TZVP', 'def2-TZVP',
         'TZVPP', 'def-TZVPP', 'def2-TZVPP', 'TZVPPP', 'QZV', 'def-QZV',
         'def2-QZV', 'QZVP', 'def-QZVP', 'def2-QZVP', 'QZVPP', 'def-QZVPP',
         'def2-QZVPP', '(7s3p)[3s2p]', '(7s3p)[4s2p]', '(9s5p)[5s3p]',
         '(11s7p)[6s4p]', '(13s8p)[8s5p]', '10s6p-dun', '10s6p1d-dun',
         '10s6p2d-dun', '6-31G*', '6-311G', '6-311G*', '6-311G**',
         '6-311++G**']

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputCheckError(Error):
    """
    Error in input parsing

    Attributes:
        expr -- input expression that failed parsing
        msg  -- explanation of error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg


class ControlFileError(Error):
    """
    General error with the control file
    Attributes:
        msg -- explanation of error
        e   -- error statement
    """

    def __init__(self, msg, e):
        self.msg = msg
        self.e = e


class FileAccessError(Error):
    """
    Error reading file
    Attributes:
        msg     -- explanation of error
        badfile -- file with error
        e       -- error statement
    """

    def __init__(self, badfile, e):
        self.badfile = badfile
        self.e = e


def is_positive_int(num):
    """Test the input to be a positive integer"""
    if is_int(num):
        if int(num) >= 0:
            return True
        else:
            return False
    else:
        return False


def is_positive_float(num):
    """Test the input to be a positive float"""
    if is_float(num):
        if float(num) >= 0:
            return True
        else:
            return False
    else:
        return False


def is_int(num):
    """Test the input num to be an int. Return True/False"""
    try:
        int(num)
        return True
    except ValueError:
        return False


def is_float(num):
    """Test the input num to be a float. Return True/False"""
    try:
        float(num)
        return True
    except ValueError:
        return False


def check_args(iargs):
    """
    Check the passed in argslist agains the dictionary of known args & return
    args as a dict.
    """
    args = dict()
    for line in iargs:
        line = line[1:]
        arg = line.split('=', 1)
        if arg[0].lower() in ARGLIST:
            if arg[0] == 'arch' or arg[0] == 'architecture' or arg[0] == 'para_arch':
                if arg[1] in PARA_ARCH:
                    args[arg[0].lower()] = arg[1]
                elif arg[1].upper() in PARA_ARCH:
                    args[arg[0].lower()] = arg[1].upper()
                else:
                    logging.warning("Invalid value of '{}' for {}.".format(
                        arg[1],
                        arg[0]
                        )
                    )
                    raise InputCheckError(
                        line,
                        'Invalid value {} for argument {}.'
                            .format(arg[1], arg[0])
                        )

            elif arg[0] == 'maxcycles' or arg[0] == 'iterations':
                if is_positive_int(arg[1]):
                    args['iterations'] = arg[1]
                else:
                    logging.warning(
                        "Invalid value of '{}' for maxcycles.".format(
                        arg[1],
                        )
                    )
                    raise InputCheckError(
                        line,
                        'Invalid value {} for argument maxcycles.'
                            .format(arg[1])
                        )

            elif (arg[0] == 'nproc' or arg[0] == 'nprocessors' or
                  arg[0] == 'nprocshared'):
                if is_positive_int(arg[1]):
                    if int(arg[1]) < 9:
                        args[arg[0].lower()] = arg[1]
                    else:
                        logging.warning("Invalid value of '{}' for {}.".format(
                            arg[1],
                            arg[0]
                            )
                        )
                        raise InputCheckError(
                            line,
                            'Invalid value {} for argument {}.'
                            .format(arg[1], arg[0])
                            )
                else:
                    logging.warning("Invalid value of '{}' for {}.".format(
                        arg[1],
                        arg[0]
                        )
                    )
                    raise InputCheckError(
                        line,
                        'Invalid value {} for argument nproc.'
                        .format(arg[1])
                        )

            elif arg[0] == 'cosmo':
                if len(arg) > 1:
                    if arg[1].lower() in DIELECTRICS:
                        args['cosmo'] = DIELECTRICS[arg[1].lower()][2]
                        logging.debug("cosmo set to {}".format(args['cosmo']))
                    elif arg[1] == '' or arg[1] == 'None':
                        args['cosmo'] = ''
                    elif is_positive_float(arg[1]):
                        args['cosmo'] = arg[1]
                        logging.debug("cosmo set to {}".format(args['cosmo']))
                    elif slug(arg[1]) in (slug(key) for key in DIELECTRICS):
                        #slugs match. good enough.
                        args['cosmo'] = (DIELECTRICS[key][2] for key in DIELECTRICS if slug(key) == slug[arg[1]])
                        logging.debug("cosmo set to {}".format(args['cosmo']))
                    else:
                        logging.warning("Solvent not found. Ignoring Cosmo")
                else:
                    #Cosmo called with no arg = no solvent
                    args['cosmo'] = ''  # epsilon = infinity is default for cosmo

            elif arg[0] == 'autocontrolmod':
                if not 'mod' in args:
                    args['mod'] = True
                else:
                    logging.warning("More than one control modify flag passed.")
                    raise InputCheckError(
                        line,
                        'More than one control modify flag passed.'
                        )

            elif arg[0] == 'nocontrolmod':
                if not'mod' in args:
                    args['mod'] = False
                else:
                    logging.warning("More than one control modify flag passed.")
                    raise InputCheckError(
                        line,
                        'More than one control modify flag passed.'
                        )

            elif arg[0] == 'rt':
                if is_int(arg[1]) and 0 <= int(arg[1]) and int(arg[1]) <= 168:
                    args['rt'] = int(arg[1])
                else:
                    args['rt'] = 168
                    logging.warning("Invalid value of '{}' for {}.".format(
                        arg[1],
                        arg[0]
                        ))
        elif arg[0].lower() not in DISCARDARGLIST:
            logging.warning("Invalid arg: {}.".format(arg[0]))
            raise InputCheckError(line, 'Invalid argument {}.'.format(arg[0]))
    return args


def check_route(route):
    """
    Check the passed in routecard and split it to components, return a dict
    of the results
    """
    route_opts = dict()
    route = route.replace('(', ' ').replace(')', '')
    route = route.replace('/', ' ')
    inroute = route.split()
    inroute = inroute[1:]
    for item in inroute:
        if item.lower() in ROUTELIST:
            if not 'jobtype' in route_opts:
                route_opts['jobtype'] = item.lower()
            else:
                if item.lower() == 'opt' and route_opts['jobtype'] == 'freq':
                    route_opts['jobtype'] = 'optfreq'
                elif item.lower() == 'freq' and route_opts['jobtype'] == 'opt':
                    route_opts['jobtype'] = 'optfreq'
                elif item.lower() == 'ts' and route_opts['jobtype'] == 'freq':
                    route_opts['jobtype'] = 'ts'
                elif item.lower() == 'freq' and route_opts['jobtype'] == 'ts':
                    route_opts['jobtype'] = 'ts'
                else:
                    logging.warning("Jobtype '{}' and '{}' called".format(
                        item,
                        route_opts['jobtype']
                        ))
                    raise InputCheckError(
                        route,
                        "More than one jobtype in route. Remove duplicates."
                        .format(route_opts['jobtype'], item)
                        )

        elif item.lower() in ROUTEOPTS:
            if not item.lower() in route_opts:
                route_opts[item.lower()] = True
            else:
                raise InputCheckError(
                    route,
                    "More than one option '{}' called in route. Remove duplicates."
                    .format(route_opts[item.lower()])
                    )

        elif item.lower() in FREQOPTS:
            if not 'freqopts' in route_opts:
                route_opts['freqopts'] = item.lower()
            else:
                raise InputCheckError(
                    route,
                    "More than one frequency option called in route. Remove duplicates."
                    .format(route_opts[item.lower()])
                    )

        elif item.lower() in FUNCTIONALS:
            if not 'functional' in route_opts:
                route_opts['functional'] = item
            else:
                logging.warning(
                    "Functional '{}' and '{}' called simultaneously.".format(
                        item,
                        route_opts['functional']
                        )
                    )
                raise InputCheckError(
                    route,
                    "More than one functional in route. Remove duplicates."
                    .format(route_opts['functional'], item)
                    )

        elif item in BASIS:
            if not 'basis' in route_opts:
                route_opts['basis'] = item
            else:
                logging.warning("Basis '{}' and '{}' called".format(
                    item,
                    route_opts['basis']
                    ))
                raise InputCheckError(
                    route,
                    "More than one basis in route. Remove Duplicates.".format(
                        route_opts['basis'],
                        item
                        )
                    )
        elif item.lower() not in DISCARDROUTEOPTS:
            lowered = False
            for base in BASIS:
                if (item.lower() == base.lower() or
                    item.lower() == base.lower().replace('-','')):
                    if not 'basis' in route_opts:
                        route_opts['basis'] = base
                        lowered = True
                    else:
                        logging.warning("Basis '{}' and '{}' called".format(
                            item,
                            route_opts['basis']
                            ))
                        raise InputCheckError(
                            route,
                            "More than one basis in route. Remove Duplicates.".format(
                                route_opts['basis'],
                                item
                                )
                            )
            if not lowered:
                logging.warning("Unknown item '{}' in route".format(item))
                raise InputCheckError(
                    route,
                    "Syntax error. Unknown keyword '{}' in route.".format(item)
                    )

    return route_opts

def check_chspin(chspin):
    """Check the passed in charge and spin, return a dict"""
    ch_spin = {'ch': 0, 'spin': 1}
    vals = chspin.split()
    if len(vals) != 2:
        raise InputCheckError(ch_spin, 'Improper argument for charge and spin.')

    if is_int(vals[0]):
        if abs(int(vals[0])) > 10:
            logging.warning('Charge of {} illogical.'.format(vals[0]))
            raise InputCheckError(ch_spin, "Illogical molecule charge.")
        else:
            ch_spin['ch'] = int(vals[0])
    else:
        logging.warning('Charge of {} invalid.'.format(vals[1]))
        raise InputCheckError(
            ch_spin,
            "Charge of {} is invalid. Requres an integer.".format(vals[0])
            )

    if is_positive_int(vals[1]):
        if int(vals[1]) > 7:
            logging.warning('Illogical molecule spin: {}.'.format(vals[1]))
            raise InputCheckError(
                ch_spin,
                "Illogical molecule spin of : {}.".format(vals[1])
                )
        else:
            ch_spin['spin'] = int(vals[1])
    else:
        logging.warning('Spin of {} invalid.'.format(vals[1]))
        raise InputCheckError(
            ch_spin,
            "Spin of {} is invalid. Requres a positive integer."
            .format(vals[1])
            )

    return ch_spin


def check_geom(geom):
    """
    Checks that the geometry is in 'atom xyz' format and the atom requested is
    real. Returns in 'xyz atom' to prepare to write coord file.
    """
    coord_geom = list()
    for line in geom:
        newline = ''
        inline = line.split()
        if len(inline) > 4:
            raise InputCheckError(line, """Input Geometry should be in
                                   cartesian coordinates as 'element x y z'.""")
        if is_float(inline[1]):
            newline += str(float(inline[1])/0.52917720859)
            newline += ' '
        else:
            logging.warning('Bad Geometry line: {}'.format(line))
            raise InputCheckError(
                line,
                "Input geometry should be in cartesian format 'element x y z'."
                )
        if is_float(inline[2]):
            newline += str(float(inline[2])/0.52917720859)
            newline += ' '
        else:
            logging.warning('Bad Geometry line: {}'.format(line))
            raise InputCheckError(
                line,
                "Input geometry should be in cartesian format 'element x y z'."
                )
        if is_float(inline[3]):
            newline += str(float(inline[3])/0.52917720859)
            newline += ' '
        else:
            logging.warning('Bad Geometry line: {}'.format(line))
            raise InputCheckError(
                line,
                "Input geometry should be in cartesian format 'element x y z'."
                )
        if inline[0] in ELEMENTS:
            newline += inline[0]
        else:
            logging.warning('Bad element line: {}'.format(line))
            raise InputCheckError(line, "Input element unknown.")
        coord_geom.append(newline)
    return coord_geom


def remove_control(lines, filename='control'):
    """
    Removes select lines from control
    """

    #sanitize input to find args
    arglist = list()
    for line in lines:
        arglist.append(line.split(' ', 1)[0])

    control_file = read_clean_file(filename)

    #instead of changing, we'll delete and append.
    lines_to_delete = list()
    for arg in arglist:
        open_arg = False
        for i in range(len(control_file)):
            if str(arg) in control_file[i]:
                lines_to_delete.append(i)
                open_arg = True
            elif open_arg and '$' in control_file[i]:
                open_arg = False
            elif open_arg:
                lines_to_delete.append(i)

    logging.debug('Deleting {} lines from {} file.'.format(len(lines_to_delete),
                                                           filename))
    lines_to_delete.sort()
    lines_to_delete.reverse()

    for dline in lines_to_delete:
        del control_file[dline]

    #write the file
    try:
        with open(filename, 'w') as f:
            for line in control_file:
                f.write(line + '\n')
    except Exception as e:
        logging.warning('Error {} writing {} file'.format(e, filename))
        raise ControlFileError('Error writing new {} file'.format(filename), e)
    logging.debug('Successfully re-wrote {} file.'.format(filename))


def add_or_modify_control(lines, filename='control'):
    """
    Adds or modifies lines in control.
    """

    #lines can be args:
    #$disp
    #or arg keyword value:
    #$parallel_parameters maxtask 10000
    #Sometimes on multiple lines:
    #$parallel_parameters
    #   maxtask 10000

    #sanitize input to find args
    arglist = list()
    for line in lines:
        arglist.append(line.split(' ', 1)[0])

    remove_control(arglist, filename)

    control_file = read_clean_file(filename)

    #remove the $end at the end to write data, then add it back in afterwards.
    del control_file[-1]

    for line in lines:
        control_file.append(line)

    control_file.append('$end')

    #write the file
    try:
        with open(filename, 'w') as f:
            for line in control_file:
                f.write(line + '\n')
    except Exception as e:
        logging.warning('Error {} writing {} file'.format(e, filename))
        raise ControlFileError('Error writing new {} file'.format(filename), e)

    logging.debug('{} file successfully edited.'.format(filename))


def auto_control_mod(control_add, job):
    """Make sure all the proper flags are passed to control for the jobtype"""
    args = list()
    for line in control_add:
        args.append(line.split(' ', 1)[0])
    #lots of parallelization or ri- and marij- flags to be added
    if job.jobtype == 'opt' or job.jobtype == 'optfreq':
        if job.ri:
            if not '$ricore' in args:
                control_add.append('$ricore 0')
        if job.nproc > 1:
            if not '$parallel_parameters' in args:
                control_add.append('$parallel_parameters maxtask=10000')
            if not '$paroptions' in args:
                control_add.append(
                    '$paroptions ga_memperproc 900000000000000 900000000000'
                    )
            if job.ri:
                if not '$ricore_slave' in args:
                    control_add.append('$ricore_slave 1')

    #flag for aoforce job AND numforce
    if job.jobtype == 'aoforce' or job.jobtype == 'numforce':
        if not '$rpacor' in args and not '$maxcor' in args:
            control_add.append('$maxcor 2048')

    #numforce works better with ri and marij. Make sure they're included
    #if possible
    if job.jobtype == 'numforce':
        if not '$parallel_parameters' in args:
            control_add.append('$parallel_parameters maxtask=10000')
        if not '$paroptions' in args:
            control_add.append(
                '$paroptions ga_memperproc 900000000000000 900000000000'
                )
        if not '$ri' in args:
            control_add.append('$ri')
        if not '$marij' in args:
            control_add.append('$marij')
        if not '$ricore' in args:
            control_add.append('$ricore 0')
        if not '$ricore_slave' in args:
            control_add.append('$ricore_slave 1')

    if job.disp:
        control_add.append('$disp')

    if job.jobtype == 'opt' or job.jobtype == 'freq' or job.jobtype == 'ts' or job.jobtype == 'sp':
        control_add.append('$scfiterlimit 100')

    return control_add


def slug(s):
    """
    Slugify a string.

    Example:
        Catalyst Bidentate Chloride 3   --> catalyst-bidentate-chloride-3
        Catalyst + Gasses               --> catalyst-gasses
    """
    
    s.replace("'", '')
    try:
        slug = unicodedata.normalize('NFKD', unicode(s))
    except UnicodeDecodeError:
        return ''   
    slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '-', slug)
    return slug


def read_clean_file(filename):
    """Reads in a file, cleaning line endings and returning a list of lines"""
    try:
        with open(filename, 'r') as f:
            ilines = f.readlines()
    except Exception as e:
        raise FileAccessError("Error reading file {}.".format(filename), e)
    logging.debug('{} read successfully'.format(filename))

    lines = list()
    for line in ilines:
        lines.append(line.strip())

    return lines


def write_file(filename, lines):
    """Writes a file 'filename' from lines"""
    try:
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line + '\n')
    except Exception as e:
        raise FileAccessError("Error writing file {}.".format(filename), e)
    logging.debug('{} written successfully'.format(filename))

    return lines


def check_files_exist(filelist):
    """Checks for the existance of file(s)"""

    for f in filelist:
        if os.path.isfile(f):
            logging.debug("'{}' file exists.".format(f))
        else:
            logging.debug("'{}' file does not exist".format(f))
            return False
        return True

def get_all_active_jobs():
    """Returns all of the jobnumbers from a qstat"""
    activejobs = list()
    qstats = Popen('qstat', stdout=PIPE).communicate()[0].split('\n')[2:]
    for stat in qstats:
        activejobs.append(stat.split(' ')[0])
    return activejobs[:-1]


def list_str(inlist):
    """Parses a list to a string with '\n' joining for logging purposes"""
    return '\n'.join(inlist)


def time_readable(timein):
    """Changes time in seconds to a readable hh:mm:ss format"""
    if not is_positive_int(timein):
        return "0"
    m, s = divmod(timein, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def check_env():
    """Checks the environment to ensure that all of the required turbomole
    variables are set. Uses defaults at top of script."""
    sets = dict()
    turbodir=os.getenv('TURBODIR')
    if not turbodir:
        sets['TURBODIR'] = MAN_TURBODIR
    turbosys=os.getenv('TURBOMOLE_SYSNAME')
    if not turbosys:
        sets['TURBOMOLE_SYSNAME'] =  MAN_TURBOSYS
    if sets:
        return sets
    else:
        return None


def get_calc_time(jobdir, jobfile):
    """Gets the job optimization time by filetime comparisons in the supplied
    job directory"""
    try:
        start = os.path.getmtime(os.path.join(os.curdir, jobdir, 'startfile'))
    except OSError:
        logging.warn('startfile not found in {}.'.format(jobdir))
        start = False
    try:
        end = os.path.getmtime(os.path.join(os.curdir, jobdir, jobfile))
    except OSError:
        logging.warn('{} not found in {}.'.format(jobfile, jobdir))
        end = False
    if start and end:
        return end - start
    else:
        return False


def get_dielectrics(inputfile):
    """Converts dielectric info from input file to python dict"""
    try:
        with open (os.path.join(os.path.dirname(sys.argv[0]), inputfile), 'r') as f:            
            data = f.readlines()
    except Exception as e:
        raise FileAccessError("Error reading file {}.".format(inputfile), e)
    
    dielectrics = dict()
    for i in range(1, len(data)):
        e = data[i].strip().split('\t')
        if not e == ['']:
            dielectrics[e[0].lower()] =[e[1],e[2],e[3],e[4],e[5],e[6]]
    return dielectrics
    
DIELECTRICS = get_dielectrics('dielectricsolvents.csv')   

