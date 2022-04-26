.. (C) British Crown Copyright 2020, Met Office.
.. Please see LICENSE.rst for license details.

.. _use_cases:

*********
Use Cases
*********

.. include:: common.txt
.. contents::
   :depth: 2

Introduction
============
The transfer package implements the archiving of |output netCDF files| after
processing and the sending of messages to an ESGF node (CEDA currently)
to start the publication process. It support several modes of operation,
depending on the state of previously archived and published files for this 
package. The different supported operation modes are described in a series
of use cases in this document. Each use case has a functional test in
the `test_command_line.py` module in the tests for this package.


Transfer Archiving Use Cases - Standard operation
=================================================
These use cases describe modes where the archiving operation is expected to 
complete successfully.

Case 1: First Archiving 
-----------------------
The first time the dataset for variable Amon/tas is archived.

Inputs:

* request.json (using UKESM1-0-LL piControl r1i1p1f2 50 year chunk as example
* mass_location = "development"
* date is 22nd July 2019
* approved variables file contains "Amon/tas" 

Data on disk:

* Directory $CDDS_DATA_DIR/output/ap5/Amon/tas/:

  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 
  
Data in MASS:

 * None

Output:

 * Data in MASS: Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/embargoed/v20190722/ :
 
  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
  * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 



Case 2: Append to embargoed data
--------------------------------
This use case decribed where data for this variable is appended to data in 
the embargoed state in MASS. This could happen when the operation is resumed
after an archiving failure or other error.

Inputs:

* request.json (using UKESM1-0-LL piControl r1i1p1f2 50 year chunk as example
* mass_location = "development"
* date is 23nd July 2019
* approved variables file contains "Amon/tas"
* version number supplied as argument is "20190722" 

Data on disk:

* Directory $CDDS_DATA_DIR/output/ap5/Amon/tas/:

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Data in MASS:

* Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/embargoed/v20190722/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc 

Output:

* Data in MASS: Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/embargoed/v20190722/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc (1)
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc (1)
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc (1)

(1) Files archived in this operation.

Case 3: Extending previously submitted dataset
----------------------------------------------
This use case is for where data has been previously submitted for a
certain period of simulation time e.g. 1850-2100, and further simulation time has 
been run that extends the period of the simulation e.g. 2100-2150.

Inputs:

* request.json (using UKESM1-0-LL piControl r1i1p1f2 50 year chunk as example
* mass_location = "development"
* date is 26th July 2019
* approved variables file contains "Amon/tas" 

Data on disk:

* Directory $CDDS_DATA_DIR/output/ap5/Amon/tas/:

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-190912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_191001-191912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_192001-192912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_193001-193912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_194001-194912.nc 

Data in MASS:

* Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20190722/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Output:

* Data in MASS
 
 * The version where the data previously was will move to state superceded.

* Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/superceded/v20190722/ :

 * files_moved.txt (1)

* Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/embargoed/v20190726/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-190912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_191001-191912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_192001-192912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_193001-193912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_194001-194912.nc 

(1) files_moved.txt should contain a list of the files that were in this location, their Adler32 checksums (obtained from moo ls -xm or similar command) and the location they have been moved to.

Case 4: Replacing previously withdrawn dataset
----------------------------------------------
This use case is for when data has previously been published, found to have 
a problem, withdrawn and now a new dataset has been produced to replace it. 

Inputs:

* request.json (using UKESM1-0-LL piControl r1i1p1f2 50 year chunk as example
* mass_location = "development"
* date is 26th July 2019
* approved variables file contains "Amon/tas" 

Data on disk:

* Directory $CDDS_DATA_DIR/output/ap5/Amon/tas/:

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Data in MASS:

* Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/withdrawn/v20190722/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Output:

* Data in MASS: Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/withdrawn/v20190722/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/embargoed/v20190726/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

CRITICAL error cases
====================
The follow use cases should all produce MASS critical errors for the 
|MIP requested variable| being processed.

Case 5 : Previously submitted
-----------------------------
Archiving data that has already been submitted .

Inputs:

* request.json (using UKESM1-0-LL piControl r1i1p1f2 50 year chunk as example
* mass_location = "development"
* date is 26th July 2019
* approved variables file contains "Amon/tas" 

Data on disk:

* Directory $CDDS_DATA_DIR/output/ap5/Amon/tas/:

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Data in MASS:

* Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20190722/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Output:

* CRITICAL error for this variable.

Case 5a : 
Archiving data that has already been partially submitted. This is a subset of the 
previously submitted use case, and is included for completeness. There is not a 
separate test for it.

Inputs:

* request.json (using UKESM1-0-LL piControl r1i1p1f2 50 year chunk as example
* mass_location = "development"
* date is 26th July 2019
* approved variables file contains "Amon/tas" 

Data on disk:

* Directory $CDDS_DATA_DIR/output/ap5/Amon/tas/:

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-190912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_191001-191912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_192001-192912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_193001-193912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_194001-194912.nc 

Data in MASS:

* Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20190722/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Output:

* CRITICAL error for this variable.

Case 6 : Different Date Stamp
-----------------------------
Archiving data when there is already data with a different date stamp in the embargoed state.

Inputs:

* request.json (using UKESM1-0-LL piControl r1i1p1f2 50 year chunk as example
* mass_location = "development"
* date is 26th July 2019
* approved variables file contains "Amon/tas"
* version number supplied as argument "20190722" 

Data on disk:

* Directory $CDDS_DATA_DIR/output/ap5/Amon/tas/:

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-190912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_191001-191912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_192001-192912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_193001-193912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_194001-194912.nc 

Data in MASS:

* Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20190615/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Output:

* CRITICAL error for this variable.

Case 7 : Used datestamp
-----------------------
Archiving additional data for a variable with a version number that has already been used in publication.

Inputs:

* request.json (using UKESM1-0-LL piControl r1i1p1f2 50 year chunk as example
* mass_location = "development"
* date is 26th July 2019
* approved variables file contains "Amon/tas"
* version number supplied as argument "20190722" 

Data on disk:

* Directory $CDDS_DATA_DIR/output/ap5/Amon/tas/:

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_190001-190912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_191001-191912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_192001-192912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_193001-193912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_194001-194912.nc 

Data in MASS:

* Directory ROOT_MASS_DIR/development/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20190722/ :

 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_185001-185912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_186001-186912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
 * tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc 

Output:

 * CRITICAL error for this variable.

