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

The transfer package is responsible for archiving the |output netcdf files|
produced by mip_convert. It should be run only after those files have been
checked by running the qc_run_and_report script in the cdds_qc module.

This package replaces a previous version of transfer. Currently the new package
only handles the arching of the output data, and the old package is still used
for sending messages to CEDA to start the puiblication process. Eventually
that functionality will also be incorporated into this module.

Code Overview
--------------

The transfer functionality is executed by running the `cdds_store` script. The
key function for this script is `store_mip_output_data` called from
`main_store`. This is the umbrella function which calls the other high level
functions. The code in this function decribes the algorithm executed by
`cdds_store`. Other modules in  this package contain the following
functionality:

* spice.py - code executed by the spice wrapper script `cdds_store_spice`, to
  facilitate running on spice.
* common.py - Some utility functions that are needed in several places in
  the transfer package.
* store.py - Most of the functionality is in this module, including gathering
  the list of variables to be archived and checking paths.
* mass.py - All functionality that interfaces with MASS is in this module.
* stored_state_checks.py - A key part of transfer is comparing the state of
  files on disk with the state of MASS for this request and variable, and
  determining what to execute based on those states. The state checks and
  decisions are in this module.

The common thread that joins the bits of code together is the list of
dictionaries which is called `mip_approved_variables` in the
`store_mip_output_data` function.  There is one dictionary per variable that
is gradually built up with all the important information to perform archiving
for that variable. The processing of gathering this information will be
described in more detail in the Execution Flow section.

At the point once the data has been gathered but before MASS commands are
executed, the dictionary for each variable should contain the following keys
(this is not an exhuastive list, there are some others that are not important
and not listed):

* `variable_id` - the |MIP requested variable name| for the this variable.
* out_var_name - The name used by CMOR when writing the |output netcdf files|,
  which is usually the same as variable ID, but is different in some cases.
  This value is taken from the approved variables list.
* `mip_table_id` - The |MIP table identifier| for this variable.
* `stream_id` - The stream that this variable is produced by and processed in.
* `date_range` - The range of dates of output data expected for this variable.
* `frequency` - The frequency of output files for this variable.
* `new_datestamp` - The datestamp used as a version number for this dataset in
  archiving and publishing.
* `output_dir` - The location on disk of the |output netcdf files| for this
  variable. This is taken from the approved variables list file produced by QC.
* `mip_output_files` - A list of paths to all the |output netcdf files| for the
  variable.
* `mass_path` - The MASS location where the |output netcdf files| for this
  variable will be archived.
* `mass_status` -The status of files on disk and in MASS, which determines what
  operations need to be performed for this variables. This value can be one
  of the values in the `MASS_STATUS_DICT` in constants.py. There is a value
  in this dictionary for each of the supported use cases as documents in the
  use_case document in the documentation for this package.
* `mass_status_suffix` -
* `stored_data` - A list of all the |output netcdf files| currently stored in
  MASS for this variable.

Execution flow
--------------

The general pattern for the cdds_store script is to build up a dictionary of
information about each variable that is to be processed including files on disk
and files in MASS, decide what MASS commands are required for that variable
based on that state information, then execute those MASS commands. The order
of tasks is:

* start by creating a list of variables to process. This contains variables
  that are both active (taken from the requested variables list) and approved
  (based on the approved variables list) are included
* get the paths of the |output netcdf files| to be archived. This is based on
  the root directory for the variable taken from the approved variables list,
  which is searched for files which match the expected filename pattern.
* construct the MASS paths for each variable
* check what files are already in MASS at the output location
* decide what operations to perform based on the state of files on disk and
  in MASS
* perform the required MASS operations

Although operations are completely independant for each variable, the current
implementation executes each step for all variables, rather all steps for
each variable. In future, this might be changed if it better for
distributed/parallel processing.


Common developement tasks
=========================

This section describes how to make changes to the code base for some common
operations.

Update/add supported use cases
------------------------------

The development of the transfer package has been centred around implementing a
series of use cases which are documented in the Use Cases document. Over
time the use cases may evolve or new ones may become apparent. In order to
implement code for a new use case, the following steps should be taken.

* add a new state to the `MASS_STATUS_DICT`.
* implement a new function in `stored_state_checks.py to check whether the new
  use case should executed. The check should take in a var_dict, which
  is the dictionary for a particular variable that contain information
  about the files on disk and in MASS for that variable, and return a string
  describing the state if the current state matches the new use case, and
  return `None` if not.
* add entries to the `MASS_PREPROC_CMD` and `DATA_FILES_FILTERS` if these
  operations are required by your use case. MASS_PREPROC_CMD is a function that
  is executed before other MASS commands to prepare MASS. An example is where
  data is being appended to previously published data. The previously published
  data must be moved to the new datestamp before the rest of the data is archived.
  DATA_FILES_FILTERS is  a command that will filter the list of files to be
  archived. An example is when appending data, the filter the names of removes
  those files already in  MASS so they are not needlessly archived a second
  time.
* add a functional test in tests/test_command_line.py

There may be other changes required if a use case is sufficiently different
from those already implemented.
