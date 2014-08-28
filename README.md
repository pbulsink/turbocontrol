# TURBOCONTROL and TURBOGO 2.0

TurboControl is a series of scripts to run Turbomole jobs from Gaussian style inputs.

Contents:

1.  Introduction
2.  System Requirements
3.  Installation
4.  TurboGo
5.  TurboControl
6.  Input Files
7.  Known Issues
8.  To Do
9.  License
10. Citing TurboControl
11. Code Details


## 1.0 Introduction
Gaussian software is well known for the user friendly GUI it contains (via GaussView). Turbomole, another computational suite, is known for its speed and optimizations, but has a significantly higher learning curve and is less beginner friendly. This software is an attempt to be able to use the user friendly input from Gaussian to smooth over the use of Turbomole. 


## 2.0 System Requirements
There are two user-facing scripts available, both written to work with Turbomole 6.1-6.5 on clusters using Grid Engine queuing software.
The only tests of operation are on a system with the following details:

- Rocks 6.1 (Emerald Boa)/CentOS 6.3
- Open Grid Scheduler/Grid Engine 2011.11p1
- Python 2.7.3

Other systems, including different operating systems, different versions of Grid Engine or python, or on other systems, are not supported.

Python dependencies include:

- pexpect 3.0
- openbabel (optional)

Prior to running TurboGo or TurboControl, a valid installation of Turbomole must be available. On systems where computational modules must be loaded, Turbomole must have been loaded to the environment. Additionally, running the Turbomole environment configuration is recommended but not required prior to launching TurboGo or TurboControl:

```bash
$ source $TURBODIR/Config_turbo_env
```

## 3.0 Installation
Installation of TurboControl is very simple. Just extract the .tar.gz file availabile from the code repository [here](http://github.com/pbulsink/turbocontrol/dist/). Alternately, the source may be downloaded from http://github.com/pbulsink/turbocontrol and used without installation.

## 4.0 TurboGo
TurboGo is a script fun on an input file. It generates the inputs required for Turbomole jobs, and submits the job to the GridEngine queue before quitting.
TurboGo is run with the following syntax:

```bash
$ turbogo [-h] [-v] [-q] file
```

positional arguments:

```
file                  Read input from gaussian-type input FILE.
```

More info on the input files is available in section 4.0, below.

optional arguments:
```bash
-h, --help            show this help message and exit
-v, --verbose         Run more verbose (show debugging info)
-q, --quiet           Run less verbose (show only warnings)
```

TurboGo saves a log file (turbogo.log) in the directory in which it is run. A second logfile (define.log) will remain if the setup crashes or is terminated at some points, or if the script is run verbose.

TurboGo writes the final coordinates to final_geometry.xyz. If openbabel is installed, it will also write finalgeom.mol. The entire optimization is written to optimization.xyz for viewing with a molecular viewer, such as vmd.


## 5.0 TurboControl
TurboControl is a management script called from a parent directory containing sub directories of input files. Each input file must be in its own directory. The input file format must be the same as the input format for TurboGo (listed above), with the extension '.in', '.inp', '.input', '.com', or '.gjf'. TurboControl reads the inputs and submits the jobs to the computational cluster queue. It then monitors running jobs to determine when the script has finished. If the job is an Opt-Freq, it prepares the frequency analysis and resubmits to the queue.
TurboControl analyzes completed Opt-Freq jobs for true optimization, and attempts to re-run jobs with modified geometries when Transition States are found. TurboControl will not get stuck on the same transition state, but will return a 'stuck' job.
TurboControl is run with the following syntax:

```bash
$ turbocontrol [-h] [-v/-q] [-s]
```

optional arguments:

```bash
-h, --help            show this help message and exit
-v, --verbose         Run more verbose (show debugging info)
-q, --quiet           Run less verbose (show only warnings)
-s, --solvent         List available solvents for COSMO and quit.
```

TurboControl outputs information every 3 hours on the status of the jobs. It writes a logfile (turbocontrol.log) and may or may not leave other log files in each directory (depending on verbosity level). Ends when the last job finishes or crashes. Requires 1 node or can be run on headnode (minimal resource consumption especially after initial job preparation and submission.)

TurboControl assists with analysis by outputting a stats file as jobs complete. This file contains file details, optimization and frequency timing details, energy, and the first frequency. Additional information can be requested by including the 'freeh' keyword (see below). 


## 6.0 Input File Format
The input file format is similar to that well known by Gaussian users. A series of keywords, one per line and indicated by a '%', is followed by the 'route card' (specific job information). Charge and spin is indicated, then the molecule is shown in Cartesian format. This is followed by optional modifications to the Turbomole Control file. Note the location of blank lines in the example (Section 5.7).

### 6.1 Keywords
Keywords are as follows:

- %nproc          - number of processors to use for the calculation job.
  - Synonym: %nprocessors
- %arch           - parallelization architecture to use for the job.
  - Synonyms: %architecture %para_arch
- %maxcycles      - number of optimization iterations before failing.
- %autocontrolmod - DEFAULT - modify the 'control' file to include optimizations to speed up the job.
- %nocontrolmod   - do not modify control file as above.
- %rt             - specify max expected runtime (for any part of job)in hours. Allows backfilling in gridengine queue to speed up job submission. For example, for a 1 hour opt and 4 hour freq, submit at least a rt of 4
- %cosmo          - use turbomole's COSMO solvation model with the specificed solvent or 'None' to use the ideal solvent (epsilon = infinity). List of available solvents can be shown by running ```turbocontrol -s```

Gaussian args, including %nosave, %rwf=[file], %chk=[file], and %mem=[memory] are silently ignored.

### 6.2 Route Card Options
Route cards take the form of the following:

\# [jobtype(s)] [joboption(s)]

Job types available:

- opt   - Perform a geometry optimization
- freq  - Perform a frequency analysis. Specify method via numforce or aoforce  
  - default = numforce
- sp    - Perform a single point energy calculation.
  - cannot be combined with Opt or Freq
- ts    - Perform a transition state search to find 1 imaginary vibration
  - cannot be combined with Opt or Freq
- prep  - Prepare the job but do not submit to queue  
  - cannot be combined with Opt or Freq

Job options available:

- ri        - Use Turbomole's ri approximation 
- marij     - Use Turbomole's marij approximation (requires ri)
- disp      - Use Turbomole's implementation of Grimme's dispersion
- aoforce   - Use aoforce for frequency jobs
- numforce  - Use numforce for frequency jobs
- freeh     - Use Turbomole's 'freeh' thermodynamics data script to extract energy infos after frequency analysis

### 6.3 Title
Following the Route cards, a blank line is added, then a line containing the title of the calculation. This can include any characters, spaces, etc., remaining on only one line. This is followed by a blank line.

### 6.4 Charge and Spin
Charge and spin are listed as two numbers:
charge spin (eg:0 1)

### 6.5 Geometry
Geometry in xyz coordinate format: Element xcoord ycoord zcoord

### 6.6 Additional control File Modifications
Additional lines to be added or removed from control. Lines automatically added are, as required,:

```bash
$ricore 0
$paroptions ga_memperproc 900000000000000 900000000000
$parallel_parameters maxtask=10000
$ricore_slave 1
$maxcor 2048

```

Additional lines may be added, or lines removed, by placing them after the geometry with a $ (for addition) or -$ (for removal).

### 6.7 Example Input Files
An example input file for benzene:

```bash
%nproc=4
%arch=GA
%maxcycles=250
%rt=6
# opt freq b3-lyp/def2-TZVP ri marij numforce

Benzene Optimization & Frequency

0 1
C  0.000  1.396  0.000
C  1.209  0.698  0.000
C  1.209 -0.698  0.000
C  0.000 -1.396  0.000
C -1.209 -0.698  0.000
C -1.209  0.698  0.000
H  0.000  2.479  0.000
H  2.147  1.240  0.000
H  2.147 -1.240  0.000
H  0.000 -2.479  0.000
H -2.147 -1.240  0.000
H -2.147  1.240  0.000

$disp
-$paraoptions

```


## 7.0 Known Issues
Current Known issues are:
- testing issues

Won't Fix includes:
- Software doesn't avoid lone proton jobs (H+), but crashes them out

Please use the Issue Tracker to post suggestions, enhancements, bugs, and modifications.

## 8.0 ToDo
High Priority:
- Distutil Inclusion
    
Medium Priority:
- MP2 and CC2 calculations
    
Low Priority:
- Presentation of badly formatted input files to allow for modification and resubmission to reduce loss by typos
- Expand inclusion of more basis sets, mix basis sets for different atoms.


## 9.0 License
All third party software is a registered trademark of their respective creators. Use of third party software via this software is limited by the conditions as laid out by the respective companies. License to use this software in no way acts as a license to use any other separate referenced software.

The MIT License (MIT)

Copyright (c) 2014 Philip Bulsink

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 10.0 Citing TurboControl
TurboControl, Turbogo, or any other parts of this code may be cited as:

Bulsink, Philip. TurboControl, v. 2.0. http://github.org/pbulsink/turbocontrol (accessed August 2014)

Change the version number to match the version that you used, and change the accessed date to when you installed or downloaded TurboControl. 

You may also reference by DOI: 10.5281/zenodo.10333

## 11.0 Code Details
Test Coverage:

Name                 Statements Missing Excluded Coverage
cosmo_op	                  106	    70	      1	    34%
test_cosmo_op	               17	     1	      0	    94%
def_op	                    302	   226	      1	    25%
test_def_op	                 20	     1	      0	    95%
freeh_op	                  162	    55	      1	    66%
test_freeh_op	               27	     1	      0	    96%
screwer_op	                 71	    25	      1	    65%
test_screwer_op	             11	     1	      0	    91%
test_all	                   18	     0	      0	   100%
turbocontrol	              537	   319	      0	    41%
test_turbocontrol	          245	    24	      0	    90%
turbogo	                    343	   132	      0	    62%
turbogo_helpers	            383	    52	      0	    86%
test_turbogo_helpers	      274	     2	      0	    99%
test_turbogo	               98	     1	      0     99%
                           2614	   910	      4	    65%

Results are low for def_op, screwer_op, cosmo_op, freeh_op, turbocontrol, and turbogo because they contain many lines of interacting with GridEngine or Turbomole. Testing is performed via monitoring the status of the scripts as they run in real conditions. 

Pylint Scores:
test_all.py             - 2.22/10
turbogo.py              - 8.80/10
test_turbogo.py         - 6.97/10
turbocontrol.py         - 8.55/10
test_turbocontrol.py    - 7.18/10
turbogo_helpers.py      - 8.81/10
test_turbogo_helpers.py - 7.45/10
def_op.py               - 8.18/10
test_def_op.py          - 5.71/10
screwer_op.py           - 7.36/10
test_screwer_op.py      - 6.67/10
freeh_op.py             - 8.71/10
test_freeh_op.py        - 6.79/10
cosmo_op.py             - 8.22/10
test_cosmo_op.py        - 6.67/10

