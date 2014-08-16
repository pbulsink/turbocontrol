#!/usr/bin/env python

from distutils.core import setup
from glob import glob

scripts = glob('bin/*')

setup(name='turbocontrol',
      version='2.0',
      description='Job Submitter and manager for TurboMole',
      long_description=open('README.md').read(),
      author='Philip Bulsink',
      author_email='philip.bulsink@uottawa.ca',
      license='MIT',
      url='http://github.com/pbulsink/turbocontrol',
      packages=['turbocontrol'],
      scripts=scripts,
      requires=['pexpect'],
      classifiers=["Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   "Development Status :: 4 - Beta",
                   "Intended Audience :: Science/Research",
                   "License :: OSI Approved :: MIT Licence",
                   "Operating System :: Unix",
                   "Environment :: Console",
                   "Topic :: Scientific/Engineering :: Chemistry",
                   "Topic :: System :: Monitoring"])
