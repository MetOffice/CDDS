.. (C) British Crown Copyright 2020, Met Office.
.. Please see LICENSE.rst for license details.

.. _developer_guide:

***************
Developer Guide
***************

.. include:: common.txt
.. contents::
   :depth: 2

Introduction
============

The cdds_convert package is responsible for setting up and launching the
CDDS rose/cylc processing suites. The cores of these suites is running
mip_convert tasks to convert from |model output files| to
|output netcdf files|. To manage compute resources, this processing is broken
down into multiple parallel tasks in several way, including by stream, grid
and time period. This allows us to break the large task of convert large volumes
of simulation data into manageable chunks of compute that fit in a reasonable
size job request on a computing cluster, such as SPICE at the Met Office.

The processing suite has also been expanded to include other tasks that
get ready for converting data or check and archive the output afterwards.
This includes running the cdds_extract script to retireve the
|model output files| from where they are stored, qc_run_and_report to check
that the |output netcdf files| comply with CMIP specified standards and
conventions, and cdds_store to archive those files in preparation for
publication.

The tasks of cdds convert include:

* retrieve source code for processing suite (u-ak283)
* gather relevant parameters from assorted configuration files such as the
  |requested variables list| and the |user configuration files| for this
  package.
* use gathered parameters correctly configure the suite for running convert
  tasks by updating the rose-suite.conf suite configuration file and the
  optional configuration file for each stream (opt/rose-suite-stream_id.conf)
  so that parallel tasks are correctly scheduled and distributed by stream,
  grid and time period.
* launch one processing suite per stream

In addition to the main processing suite setup code, there is also code in the
convert package that is run within the processing suite. These fall into
three categories:

* mip_convert wrapper - is called by the mip_convert tasks in the suite to
  set up the environment for running mip_convert
* organise files - This runs before the files are concentated to reorganise
  the files so they are grouped by stream and mip table rather than by time
  period, and also prepares a list of tasks to be executed by the
  concatenate tasks.
* concatentation - these script join the output files from mip_convert tasks
  together into longer periods of data so there are fewer files to manage.

Code Overview
--------------

The functionality for setting up and running the processing suite lives mainly
in the process/__init__.py file in the ConvertProcess class. This class
contains all the functions needed to gather together all the parameters needed
to to configure the suite for running mip_convert. The main function for
this functionality is `run_cdds_convert` in `convert.py`.


The mip_convert_wrapper code lives in the `mip_convert_wrapper`. The following
files contain code for the following functionality:

* `wrapper.py` - the main function for mip_convert_wrapper functionality.
* `file_processors.py` - parses file names to decide which input files are
  needed by this mip_convert task
* `file_management.py` - copies input and output files required by mip_convert
  tasks.

The organise files functionality live entirely in the `organise_files.py`
module. The main function for this functionality is `organise_files`.

The code for the concatenation operations live in the `concatenation`
directory in cdds_convert. There are 2 operations associated with
concentation. The first is setup, which creates a database of concatenate
tasks to perform, and the second is conctenate batch, which performs the tasks
in the task database. The code for setup lives in `concatenation_setup.py` and
the code for concatenate batch live in `concatenation/__init__.py`.


Execution flow
--------------

**cdds_convert script**
`run_cdds_convert` is the main function for this part of convert. It creates a
ConvertProcess object and calls the following functions:

* `validate_streams` - check what streams are to be executed.
* `checkout_convert` - gets the source code of the suite from the repository
* `update_convert_suite_parameters` - prepare the convert suite for processing.

The processing suite for each stream is then launched by calling
`submit_suite` for each stream to be processed.

**run_mip_convert script**
The `run_mip_convert_wrapper` function in `wrapper.py` calls the following
functions:

* `calculate_mip_convert_run_bounds` - calculate how long the period of time to
  be processed is.
* `get_paths` - Get the file paths for the files to be used by mip_convert for
  this cycle
* `copy_to_staging_directory` - copy the mip_convert input files to the
  staging directory if a staging directory is being used.
* `setup_cfg_file` - Fill in the parameters in the template
  |User configuration files| to be used by mip_convert for this operation.
* `run_mip_convert` - Run the mip_convert script
* `manage_logs` - Copy the mip_convert logs to convert proc directory
* `manage_critical_issues` - Ensure critical issues from mip_convert are
  copied to the convert critical issues file.

**mip_concatenate_organise script**
The mip_concatenate_organise script changes how the files produced by
mip_convert are stored, placing them into a different directory structure
that is closer to the structure required for the final output. The main
function is `organise_files`, which calls:

* `transpose_directory_structure` - find all the output files from mip_convert
  that need to be moved, create new directories and move files.
* `write_mip_concatenate_cfg` - Write the concatenate settings to a file ready
  to be used by the concatenate operation.

**mip_concatenate_setup script**
The main function for mip_concatenate_setup is concatenate_setup. This
function first calls `build_concatenation_work_dict` to  determine what
concatenate tasks need to be performed. This is done seprately from actually
performing the tasks so if the script fails it can resubmitted and only the
tasks that have not been performed will be run in subsequent executions. These
tasks are written into a work database by `write_concatenation_work_db`,
which is used by the mip_concatenate script.

**mip_concatenate script**
The main function for the `mip_concatenate` script which performs the
concatenate tasks is `batch_concatenation`. It iterates through the
concatenation tasks in the database created by mip_concatenation_setup. For
each task in the database, if calls `concatenation_task`.


Common developement tasks
=========================

This section of the guide gives high level instructions on how to perforrm
common development tasks when developing the convert code.

Update resources
----------------

The allocation of resources to convert tasks is determined by values stored in
the `constants.py` file. The important values are:

* `MIP_CONVERT_MEMORY` - The amount of memory allocated to each mip_convert
  task. Values are per model and stream.
* `MIP_CONVERT_TEMP_SPACE` - The amount of high speed temporary disk space
  allocated for each mip_convert tasks. Values are per model and stream.


Update cycling lengths
----------------------

There are two processing cycles in a CDDS processing suite. The first is the
mip_convert cycle. One mip_convert tasks runs per cycle and produces
one output file per variable per cycle. The second is concentation cycles.
One mip_concatenate tasks is run per cycle, but different number of files are
produced for each variable in a cycle based o the size of a variable. The cycle
length is determined by the cycle length of the variable with longest
concatenate cycle length. Cycle lengths can be adjusted as follows:

* `MIP_CONVERT_CYCLE_LENGTHS` - The length time for which data is processed by
  a single mip_convert task. Values are per model and stream.
* `SIZING_INFO` - The length time for each output file for each variable is
  based on the size of the dimensions of the data being converted. concatenate
  will look for the closest match for the relevant model and divide the time
  bounds of the processing run to produce output files of the correct length.
