#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""
Simple operating code for Turbomole
Reads input, sets up job via define, generates the submit script
depending on number of cores requested, and submits.
Future watch jobs & do sequential calculations (ie opt then freq).
Input files are formatted as gaussian, with additional/alternative keywords.
"""
from src.turbogo_src import *
import argparse
import logging
import sys
import src.turbogo_helpers
import os


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
