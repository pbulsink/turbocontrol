#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

from src.turbocontrol_src import *
import src.turbogo_helpers
import logging
import argparse
from time import time
import os, sys

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
    