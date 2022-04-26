.. (C) British Crown Copyright 2018, Met Office.
.. Please see LICENSE.rst for license details.

.. _overview:

CDDS QC
=======

.. include:: common.txt

The CDDS QC package enables a user to check whether the
|output netCDF files| conform to the WGCM CMIP standards.

An overview of CDDS QC
----------------------

CDDS QC is built upon the IOOS Compliance checker (link required) and uses
plugins to include CF-1.7 standards testing and CMIP6 requirements.

When running against a netCDF dataset, CDDS QC checks the following:
    * The file names are consistent with their contents.
    * All relevant global and variable attributes correspond to the CMIP6
      Controlled Vocabularies and |MIP tables| and are present if required.
    * There are no temporal gaps in the data, i.e. missing time records, and
      there are no files missing.
    * The dataset conforms to the CF-1.7 standard (link needed).

The result of the QC run is saved to a database, and also can be viewed via a
report in json format.
