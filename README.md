# TURBOCONTROL and TURBOGO 1.0

TurboControl is a series of scripts to run Turbomole jobs from Gaussian style inputs.

Contents:

1.  Introduction
2.  System Requirements
3.  TurboGo
4.  TurboControl
5.  Input Files
6.  Known Issues
7.  To Do
8.  License


## 1.0 Introduction
Gaussian software is well known for the user friendly GUI it contains (via GaussView). Turbomole, another computational suite, is known for its speed and optimizations, but has a significantly higher learning curve and is less beginner friendly. This software is an attempt to be able to use the user friendly input from Gaussian to smooth over the use of Turbomole. 


## 2.0 System Requirements
There are two user-facing scripts available, both written to work with Turbomole 6.1 on clusters using Grid Engine queuing software.
The only tests of operation are on a system with the following details:

- Rocks 6.1 (Emerald Boa)/CentOS 6.3
- Open Grid Scheduler/Grid Engine 2011.11p1
- Python 2.7.3

Other systems, including different operating systems, different versions of Grid Engine or python, or on other systems, are not supported.

Python dependencies include:

- pexpect 3.0

Prior to running TurboGo or TurboControl, a valid installation of Turbomole must be available. On systems where computational modules must be loaded, Turbomole must have been loaded to the environment. Additionally, running the Turbomole environment configuration is recommended but not required prior to launching TurboGo or TurboControl:

```bash
$ source $TURBODIR/Config_turbo_env
```


##3.0 TurboGo
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
```
-h, --help            show this help message and exit
-v, --verbose         Run more verbose (show debugging info)
-q, --quiet           Run less verbose (show only warnings)
```

TurboGo saves a log file (turbogo.log) in the directory in which it is run. A second logfile (define.log) will remain if the setup crashes or is terminated at some points, or if the script is run verbose.


##4.0 TurboControl
TurboControl is a management script called from a parent directory containing sub directories of input files. Each input file must be in its own directory. The input file format must be the same as the input format for TurboGo (listed above), with the extension '.in'. TurboControl reads the inputs and submits the jobs to the computational cluster queue. It then monitors running jobs to determine when the script has finished. If the job is an Opt-Freq, it prepares the frequency analysis and resubmits to the queue.
TurboControl analyzes completed Opt-Freq jobs for true optimization, and attempts to re-run jobs with modified geometries when Transition States are found. TurboControl will not get stuck on the same transition state, but will return a 'stuck' job.
TurboControl is run with the following syntax:

```bash
$ turbocontrol [-h] [-v] [-q]
```

optional arguments:

```
-h, --help            show this help message and exit
-v, --verbose         Run more verbose (show debugging info)
-q, --quiet           Run less verbose (show only warnings)
```

TurboControl outputs information every 3 hours on the status of the jobs. It writes a logfile (turbogo.log) and may or may not leave other log files in each directory (depending on verbosity level). Ends when the last job finishes or crashes. Requires 1 node or can be run on headnode (minimal resource consumption especially after initial job preparation and submission.)

TurboControl assists with analysis by outputting a stats file as jobs complete. This file contains file details, Optimization and frequency timing details, energy, and the first frequency.


## 5.0 Input File Format
The input file format is similar to that well known by Gaussian users. A series of keywords, one per line and indicated by a '%', is followed by the 'route card' (specific job information). Charge and spin is indicated, then the molecule is shown in Cartesian format. This is followed by optional modifications to the Turbomole Control file. Note the location of blank lines in the example (Section 5.7).

### 5.1 Keywords
Keywords are as follows:

- %nproc          - number of processors to use for the calculation job.
  - Synonym: %nprocessors
- %arch           - parallelization architecture to use for the job.
  - Synonyms: %architecture %para_arch
- %maxcycles      - number of optimization iterations before failing.
- %autocontrolmod - DEFAULT - modify the 'control' file to include optimizations to speed up the job.
- %nocontrolmod   - do not modify control file as above.

Gaussian args, including %nosave, %rwf=[file], %chk=[file], and %mem=[memory] are silently ignored.

### 5.2 Route Card Options
Route cards take the form of the following:

\# [jobtype(s)] [joboption(s)]

Job types available:

- opt   - Perform a geometry optimization
- freq  - Perform a frequency analysis. Specify method via numforce or aoforce  
  - default = numforce
- prep  - Prepare the job but do not submit to queue  
  - cannot be combined with Opt or Freq

Job options available:

- ri        - Use Turbomole's ri approximation 
- marij     - Use Turbomole's marij approximation (requires ri)
- disp      - Use Turbomole's implementation of Grimme's dispersion
- aoforce   - Use aoforce for frequency jobs
- numforce  - Use numforce for frequency jobs

### 5.3 Title
Following the Route cards, a blank line is added, then a line containing the title of the calculation. This can include any characters, spaces, etc., remaining on only one line. This is followed by a blank line.

### 5.4 Charge and Spin
Charge and spin are listed as two numbers:
charge spin (eg:0 1)

### 5.5 Geometry
Geometry in xyz coordinate format: Element xcoord ycoord zcoord

### 5.6 Additional control File Modifications
Additional lines to be added or removed from control. Lines automatically added are, as required,:

```
$ricore 0
$paroptions ga_memperproc 900000000000000 900000000000
$parallel_parameters maxtask=10000
$ricore_slave 1
$maxcor 2048
$les all 1
```

Additional lines may be added, or lines removed, by placing them after the geometry with a $ (for addition) or -$ (for removal).

###5.7 Example Input Files
An example input file for benzene:

```
%nproc=4
%arch=GA
%maxcycles=250
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


## 6.0 Known Issues
Current Known issues are:
- none

Won't Fix includes:
- Software doesn't avoid lone proton jobs (H+), but crashes them out


## 7.0 ToDo
High Priority:
- Transition state and TD-DFT calculations may require expansion of the def-op script or modification of input files.
    
Medium Priority:
- none
    
Low Priority:
- Presentation of badly formatted input files to allow for modification and resubmission to reduce loss by typo
- Expand inclusion of more basis sets, mix basis sets for different atoms.


## 8.0 License
All third party software is a registered trademark of their respective creators. Use of third party software via this software is limited by the conditions as laid out by the respective companies. License to use this software in no way acts as a license to use any other separate referenced software.

This software is copyright with the BSD License

Copyright (c) 2014, Philip Bulsink
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## 9.0 Code Details
Test Coverage:

Name                 Statements Missing Excluded Coverage
def_op	                272	    203	      1	        25%
def_op_test	            17	    1	        0	        94%
screwer_op	            71	    25	      1	        65%
screwer_op_test	        11	    1	        0	        91%
test_all	              16      0	        0	        100%
turbocontrol	          384	    240	      0	        38%
turbocontrol_test	      188	    21	      0	        89%
turbogo	                294	    125	      0	        57%
turbogo_helpers	        306	    42	      0	        86%
turbogo_helpers_test	  247	    2	        0	        99%
turbogo_test	          84	    1	        0	        99%
TOTAL:	                1890	  661	      2	        65.0

Results are low for def_op, screwer_op, turbocontrol, and turbogo because they
contain many lines of interacting with GridEngine or Turbomole. Testing is
performed via monitoring the status of the scripts as they run in real
conditions.

Pylint Scores:
test_all.py             - 2.50/10
turbogo.py              - 8.28/10
turbogo_test.py         - 7.14/10
turbocontrol.py         - 8.42/10
turbocontrol_test.py    - 8.19/10
turbogo_helpers.py      - 9.08/10
turbogo_helpers_test.py - 7.85/10
def_op.py               - 8.23/10
def_op_test.py          - 6.11/10
screwer_op.py           - 7.36/10
screwer_op_test.py      - 6.67/10

