.. (C) British Crown Copyright 2019, Met Office.
.. Please see LICENSE.rst for license details.

.. _user_guide:

**********
User Guide
**********

.. include:: common.txt
.. contents::
   :depth: 2

Introduction
============
The transfer package of CDDS is responsible for storing the |Output netCDF files| in the archive
ready for publishing, as well as sending messages to CEDA/ESGF to trigger the start of the 
publication process that includes pulling the data onto ESGF nodes and making it publicly available.
The steps include:

 * check what |MIP output variables| are ready for publication
 * for each variable to be published:

  * create a list of |output netCDF files| to be published
  * check the state of files already in the archive 
  * compare the files to be archived with those in the archive and check this is a valid operation
  * if a valid operation, decide what operations need to be performed based on the files on disk and in the archive
  * perform the required archiving operations (for the Met Office, these are mass commands)
  * send message to CEDA/ESGF to start the publication process. This part is done separately from the rest as processing should be reviewed before publication.

Quick Start
===========

The transfer package works on the output from the convert and quality control steps of the CDDS
processing pipeline. Information on which commands to run, in what order and with what arguments 
can be found in the CDDS operational procedure.
https://code.metoffice.gov.uk/trac/cdds/wiki/CDDSOperationalProcedure 

Alternatively there is a rose suite which automates the processing of package through the
CDDS pipeline. THis is also described in the operational procedure.

Once you have the run the quality control script `qc_run_and_report` for your package,
you can then run the transfer script `cdds_store`:
`cdds_store request.json --use_proc_dir`

Other useful options include:

 * `--mip_approved_variables_path` - The path to a file containing a list of variables that have passed the quality control checks and are ready to be archived.
 * `--simulate` - Do a dry run of the archiving operation. The commands that would have been run will be output to the log. 
 * `--mass_root` - The root location in the archiving for CDDS to use for storing |output netCDF files|.
