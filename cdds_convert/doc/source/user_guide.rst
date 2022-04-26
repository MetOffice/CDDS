.. (C) British Crown Copyright 2018-2019, Met Office.
.. Please see LICENSE.rst for license details.

.. _user_guide:

**********
User Guide
**********

.. include:: common.txt
.. contents::
   :depth: 2

Running CDDS Convert
====================

CDDS Convert provides the following tools:

`cdds_convert`
    CDDS Convert process initiator. Is driven using information from
    a |request| JSON file (see command help for details of arguments).
`mip_concatenate_setup`
    First component of the process to concatenate files produced by
    MIP Convert. This script scans a directory for files and identifies groups
    of files that can be concatenated. This script writes the work to be done
    to a sqlite3 database (link to structure).
`mip_batch_concatenate`
    Second component of the concatenation process. This script takes the
    database created by `mip_concatenate_setup` and executes the necessary
    commands to affect the concatenation. Concatenations are organised by
    |MIP requested variable| and can be performed using multiple threads, with
    each thread working through the operations for a single variable at a time.
    Once a concatenation is successful all source files are deleted to save
    storage space.
`mip_concatenate`
    A simple command line tool performing a single concatenation.

Command line options are described in the help for each script.



Underlying concatenation operations
===================================

Individual concatenations
-------------------------

.. _source forge: http://nco.sourceforge.net/nco.html#ncrcat-netCDF-Record-Concatenator

Files are concatenated together using the `ncrcat` command, which is part of
the nco toolset, see `source forge`_ or the corresponding man pages for details.
The compression factors (volume of source data divided by volume of resulting
data) may vary wildly from around 1.5 (data varying over several orders of
magnitude, e.g. precipitation) to around 4 (little variation in data over wide
areas, e.g. sea ice cover).

.. _concatenate_database_structure:

Concatenation database structure
--------------------------------

The concatenation database contains information on the concatenation tasks to
be performed. This information is hosted in a single table `concatenation_tasks`
which contains the following fields:

output_file `TEXT UNIQUE`
    Destination file name.
variable `TEXT`
    Variable to be processed in the form `<mip table>/<mip requested variable name>`
input_files `TEXT NOT NULL`
    Space separated list of input files to be concatenated.
start_timestamp `REAL`
    Timestamp recorded when this concatenation task is started
complete_timestamp `REAL`
    Timestamp recorded when this concatenation task finishes.
status `TEXT`
    Status of the task. Can be one of `NOT_STARTED`, `STARTED`, `COMPLETE`,
    `FAILED`.

When the database is created all records have a status of `NOT_STARTED`. When a
concatenation task begins status is updated to `STARTED` and to `COMPLETE` when
the task has finished. If a task fails it will be marked as `FAILED`.
Note that if a batch job running `mip_batch_concatenate` is terminiated records
will be left in a `STARTED` state until there is some intervention.


.. _required-input-files:

Required input files
====================

MIP convert configs
    A set of configuration files named `mip_convert.cfg.<component name>` must
    exist in the `procdir`/configure directory, where
    `<component name>` denotes different grids of the variables that can be
    processed in parallel by the conversion suite.

The `procdir`/convert/log directory must also exist


.. _sizing-file-structure:

MIP Concatenate sizing info
---------------------------

The MIP Concatenate sizing info describes the time span for which files should
be concatenated together. The duration of each output file is determined based
on its spatial shape and temporal frequency. The sizing information is
currently stored in the CDDS Convert source code.

If this sizing file was used for monthly data then single level or category
ocean and sea-ice variables (e.g. `Omon/tos` or `SImon/siconc`) which have 360
longitudes and 330 latitudes would be output in 50 year chunks, 3D atmosphere
variables would also be output in 50 year chunks, and all other monthly
variables would be output in 50 year chunks.
All 6 hourly instantaneous (frequency = `6hrPt`) variables would be concatenated
into one year chunks.

Chunk sizes should be chosen with consistency across data sets in mind, but
may be different for different models, particularly different horizontal
resolutions, in order to produce managable numbers of files and file sizes.

CDDS Convert Suite
==================

The output of the cdds_convert module is a rose suite configured to run the
tasks required to create the |MIP output variables| requested. cdds_convert
gathers togther the information required, checks out the rose suite,
updates the configuration for the |package| being run, then starts the suite
using the rose suite-run command.

The suite operates by breaking up the time span of the data
into small chunks for processing. The variables for each small time chunk are
processed togther as a single task. This produces separate variables for each
time chunk of processing for each variable. A smaller number of files minimises
file management effort. To achieve this, concatenation tasks are run once for
multiple cycles of MIP Convert to combine the output files from several cycles
into a single output file.

The following tasks are run in the suite:
 * *run_extract* - (NOT FULLY IMPLEMENTED) if the ``--run-extract`` option is
   specified on the command line to cdds_convert, an extract task is run at
   the start of the suite for each stream to get the data from MASS.
 * *mip_convert* - create a file for each |MIP output variable| from one or
   more |input variable| loaded from |Model output files|.
 * *organise_files* - reorganise files to be optimal for concatenation. The
   files output from mip_convert are organised by date, so each tasks works in
   a separate directory. organise_files moves files and directories to
   organised by MIP table.
 * *mip_concatenate_setup* - determines what output files should be produced for
   the time period covered by the concatenation task annd from what input
   files. This is written to database to keep track of which tasks have
   been performed.
 * *mip_concatenate_batch* - execute the concatenation tasks.
 * *run_qc* - (NOT FULLY IMPLEMENTED) if the ``--run-qc`` option is specified on
   the command line to cdds_convert, a quality control task is run at the end
   of the suite for each stream to run quality control checks on the data
   produced for that stream.
 * *run_transfer* - (NOT FULLY IMPLEMENTED) if the ``--run-transfer`` option is
   specified on the command line to cdds_convert, a send_to_mass task is
   run and the end of each suite (after run_qc) for the data produced by
   that stream.

cdds_convert runs one suite for each data |stream| from the models. Each of the
streams, for example ap4 or onm, is processed in its own suite. This allows for
different streams to progress at different speeds, rather than constraining
progress by the slowest stream.

The configuration of the suite is done by setting values in the rose-suite.conf
and suite optional config files in the opt directory. The settings that apply
to all streams are set in rose-suite.conf, with the per stream settings
specified in optional config files named based on the |stream identifier|
and located at ``opt/rose-suite-<stream_id>.conf``. The
``--opt-conf-key=<stream_id>`` argument is used when running each suite to specify
the stream being processed and pick up the correct settings for that stream.


Scheduling
----------
The main reason for the existence of CDDS Convert to wrap mip_convert is
the large data volumes involved require processing to be broken up into
smaller tasks and scheduled appropriately. CDDS Convert calculates how to break
the processing down into smaller tasks and when to run each of the tasks. The
Rose/Cylc workflow management tool, as used for running climate simulations,
is used by |CDDS|.

Rose/Cylc suite typically determine a frequency with which tasks should run and
then schedule those tasks at regular intervals. The CDDS suite has 2 cycle
frequencies for each of the two groups of tasks: mip_convert tasks and
concatenate tasks (organise_files, mip_concatenate_setup,
mip_concatenate_batch). The first group of tasks, the mip_convert tasks, have
a cycling frequency spciefied in the cdds config files. The second group of
tasks, the concatenate tasks which join together the output files from
mip_convert, have a cycling frequency based on the
:ref:`sizing-file-structure`, which is typically a multiple of mip_convert
cycling frequency, typically 10.

The cycles are aligned with the reference date, so that as much as possible
the output files will start and end on a date that is a multiple of time
window for each output file. For example if the reference data is 1850 and each
output file covers 50 years of data, the output files should contain data for
1950-2000, 2000-2050 etc. For some experiments, the start and end dates will
not line up with the reference date and output file time window. In this case
there may be a smaller file created for the start and end of run. For example,
if an experiment covered the period 1972-2115, wth a 50 year time window for
each output file, the files produced would cover 1972-2000, 2000-2050,
2050-2100, and 2100-2115.

The scheduling of tasks is specified in the suite.rc file of the suite, which
uses variables defined in the rose-suite.conf file. cdds_convert calculates
the scheduling parameters for each stream in a package and sets the parameters
accordingly so that the tasks will be correctly scheduled when the suite is
run.