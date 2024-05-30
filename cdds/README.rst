.. Copyright (C) British Crown (Met Office) & Contributors.
.. Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
.. See the LICENSE file in the top level of this repository for full details.

.. _overview:

CDDS
====

.. include:: common.txt

The CDDS package provides a collection of Python software libraries
for managing, processing and publishing model data and metadata.

An overview of CDDS
-------------------

The purpose of CDDS is to allow PP and netCDF data produced by the HadGEM3 and UKESM1
climate models to be converted to the CMOR compliant netCDF form required for publication
to exercises such as CMIP6.

CDDS was initially developed for CMIP6, but has been adapted to handle any other project
that follows an equivalent structure, with configuration information on the project
and models held in the cdds plugins.

CDDS requires the user to perform a few actions;
  * Construct a Request JSON file describing the |package| of processing to be performed,
    i.e. experiment, model, suite, plus various other pieces of metadata.
  * Construct a `data` and `proc` (processing) directory for CDDS to use.
  * Create the |Requested variables list| from the Request JSON file and either the 
    CMIP6 Data Request or a supplied variables list.
  * Launch the conversion process, which will:
     * Set up directories and some configuration files
     * Extract required data from MASS (optional)
     * "CMORise" data using MIP Convert in chunks of up to 5 years at a time
     * Concatenate small files together into predefined time ranges
     * Check the output for compliance with the required standards and that there
       are no gaps in time series (optional)
     * Archive data to MASS in a predefined directory structure (optional)

The full process of using CDDS is described on the wiki attached to https://github.com/MetOffice/CDDS.

