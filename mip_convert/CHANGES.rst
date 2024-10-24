.. (C) British Crown Copyright 2016-2024, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

Release 3.0.3, October 24, 2024
===============================
* Allow forced coordinate rotation. Output data will be forced to include rotated coordinates
  and true lat-lon coordinates (CDDSO-529)

Release 3.0.2, September 27, 2024
=================================
* Add functionality to remove halo columns and rows from atmosphere data (CDDSO-521)
* Add Mappings for CP4A (CDDSO-515)

Release 3.0.1, August 21, 2024
==============================
* Separated test reference data by versions in MIP Convert functional tests (CDDSO-400)
* Added a log identifier to separate log files of multiple functional tests in the same
  test class (CDDSO-476)
* Added mappings for CORDEX (CDDSO-421)

Release 3.0.0, May 15, 2024
===========================
* MIP Convert now returns exit codes correctly (CDDSO-387)
* The field `child_base_date` in the `request` section of the MIP Convert Config file has been 
  renamed for clarity to `base_date` (CDDSO-455)

Release 2.5.9, June 25, 2024
============================
* Added new MIP tables (GC3hrPtUV, GCAmon6hr, GCAmonUV, GC3hr, GC1hr) and mappings for CP4A, along with
  sizing and memory configuration tuning for new diagnostics (CDDSO-414, CDDSO-463).

Release 2.5.8, February 28, 2024
================================
* No changes

Release 2.5.7, February 21, 2024
================================
* Additional Mappings for the HadREM3-CP4A-4p5km model (CDDSO-354, CDDSO-405)

Release 2.5.6, February 09, 2024
================================
* Updated mapping for fco2nat to use anomalous LBTIM code in UKESM model data.
  This change makes no difference to the output data, but keeps consistency
  with previous CMIP6 data production (CDDSO-394)
* Added GCAmon6hr/tas mapping (tas, but with monthly means sampled every 6 hours) to GCModel Dev (CDDSO-389)
* Added new variables for UKCP to GCModelDev (CDDSO-388)

Release 2.5.5, January 18, 2024
===============================
* Issues with incorrect/inconsistent LBFT codes in PP data (section 3) should no
  longer break processing (CDDSO-383)

Release 2.5.4, December 13, 2023
================================
* Fix the `reference_date` parsing logic for variables defined with a forecast time dimension (CDDSO-363)
* Implement annual ocean diagnostics for the `GCOyr` MIP table (CDDSO-369)

Release 2.5.3, November 22, 2023
================================
* Adaptations needed for new CMIP6Plus MIP tables (CDDSO-336, CDDSO-365)
* Update to version of CMOR to 3.6.3 (CDDSO-368)

Release 2.5.2, October 18, 2023
===============================
* Polar row masking is now specified directly in the MIP Convert config
  files (CDDSO-331)
* Upgraded CMOR to version 3.7.3, which now permits much larger arrays
  to be passed for writing without segfaulting (CDDSO-357)

Release 2.5.1, August 4, 2023
=============================
* Add ``zos`` mapping for HadGEM3-GC3p05-N216ORCA025 (CDDSO-328)

Release 2.5.0, July 27, 2023
============================
* Updated CMOR to version 3.7.2, which required iris update to 3.4.1 (CDDSO-321)
* Relocated test data to enable testing on multiple platforms (CDDSO-278)
* Change date format in config file to ISO datetime (CDDSO-294, CDDSO-313)

Release 2.4.6, June 23, 2023
============================
* Add Eday/evspsbl mapping to MIP Convert (CDDSO-291)

Release 2.4.5, May 22, 2023
===========================
* MIP Convert can now correctly output data from CICE daily streams where the time coordinate 
  data is faulty, and SIday/siconc can be produced (CDDSO-277)

Release 2.4.4, May 4, 2023
=============================

* No changes

Release 2.4.3, March 31, 2023
=============================

* Add a ``--relaxed-cmor`` option to ``mip_convert``. When used certain metadata fields e.g.
  experiment_id are not checked against the controlled vocabularies (CDDSO-252).
* All ancillary STASH codes are now correctly treated as time invariant (CDDSO-247).


Release 2.4.2, March 1, 2023
============================

* Add mappings for `zostoga` diagnostic in the UKCP18 GC3p05-N216ORCA025
  model configuration (CDDSO-239)

Release 2.4.1, January 18, 2023
===============================

* Implement a `mask_slice` option in configuration file for providing ocean data masks (CDDSO-67, 215)
* Add support for the UKCP18 GC3p05-N216ORCA025 model and UV grid mappings (CDDSO-222)

Release 2.4.0, September 12, 2022
=================================

* Move test execution from nose to pytest (CDDSO-128)

* Refactor functional tests (CDDSO-76, 170)

Release 2.3.2, September 01, 2022
=================================

* MIP Convert can now produce files with a forecast time coordinate as introduced
  at CMOR v3.7.0 (CDDSO-124)
* Approved mapping for fsitherm (CDDSO-163)

Release 2.3.1, June 29, 2022
============================

* Add extra pressure levels for UKCP (CDDSO-146)

Release 2.3.0, May 24, 2022
============================

* Development moved to github
* Duplicate coordinates error rased when producing certain variables is now not raised (CDDSO-109)

Release 2.2.5, May 4, 2022
============================

* No changes

Release 2.2.4, April 22, 2022
=============================

* No changes

Release 2.2.3, April 7, 2022
============================

* No changes

Release 2.2.2, March 18, 2022
=============================

* CV checks for non-CMIP6 processing is now the same as for CMIP6 (#2539)
* Additional mappings for UKCP (#2518)

Release 2.2.1, February 15, 2022
================================

* No changes.

Release 2.2.0, February 9, 2022
===============================

* Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* Update to use python 3.8 (#2438)
* Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* Retired umfilelist and all connected code (#2438)

Release 2.1.2, November 25, 2021
================================

* ``mip_convert`` now can handle `LBTIM` constraints correctly (#2455)

Release 2.1.1, October 26, 2021
===============================

* Added regional model variable mappings for CORDEX (#2442)

Release 2.1.0, September 6, 2021
================================

* No changes.

Release 2.0.8, August 3, 2021
=============================

* Refactored ``mip_convert`` to improve performance (#2423)

Release 2.0.7, July 15, 2021
============================

* No changes.

Release 2.0.6, June 29, 2021
============================

* No changes.

Release 2.0.5, June 11, 2021
============================

* No changes.

Release 2.0.4, May 17, 2021
===========================

* Added approved mappings for depth integrated upper ocean (top 100m) biogeochemistry
  variables (#2146)

Release 2.0.3, April 28, 2021
=============================

* No changes.

Release 2.0.2, April 22, 2021
=============================

* Approved mappings for ``E3hrPt/ts``, ``CFmon/ta``, ``CFday/ta`` and ``CFday/ta700`` diagnostics (#2303, #2326)
* Fixed a bug in MIP Convert which prevented it from providing CMOR with correct Controlled Vocabulary file (#2317)

Release 2.0.1, March 25, 2021
=============================

* MIP Convert now allows seasonal mean data to be produced (#943)

Release 2.0, February 24, 2021
==============================

* Updated CDDS codebase to Python 3.6.

Release 1.6.5, February 22, 2021
================================

* No changes.

Release 1.6.4, February 11, 2021
================================

  * No changes.

Release 1.6.3, February 9, 2021
===============================

* MIP Convert can now produce monthly mean diurnal cycle diagnostics (#349)
* Added processor for loaddust (#1823)
* Approved several mappings (#2220)

Release 1.6.2, January 11, 2021
===============================

* Approved mappings for ``mc``, ``mcd`` and ``mcu`` diagnostics (#2177)

Release 1.6.1, November 26, 2020
================================

* No changes.

Release 1.6.0, November 05, 2020
================================

* Fixed processors for vertical integrals of ocean biogeochemical variables (#1192)
* Corrected ``jpdftaure*`` diagnostics related to the cloud area fraction in
  the atmosphere layer (#558, #2091)
* Added several new mappings (#1822, #1845, #1846) and updated review statuses (#2090)

Release 1.5.5, October 20, 2020
===============================

* No changes.

Release 1.5.4, October 7, 2020
==============================

* No changes.

Release 1.5.3, September 16, 2020
=================================

* No changes.

Release 1.5.2, September 4, 2020
================================

* No changes.

Release 1.5.1, August 20, 2020
==============================

* Corrections to vertical coordinate data in some CFsubhr radiation mappings
  (#1946)
* Approval of several mappings (#1975) and removal of ok status from one
  (#1992)

Release 1.5.0, July 2, 2020
===========================

* Corrected mappings for ``wbptemp`` and ``rsut*4co2`` (#567, #1502)
* Added many new mappings (#848, #1691, #1803, #1820) and updated review
  statuses (#1855)
* Added mappings for CF sites variables (#1838)
* ``zostoga`` can now be produced for HadGEM3-GC31-MM (#1266)
* ``evs`` can now be marked as active by CDDS Prepare following alterations to
  the mapping, which avoids an issue when reading the NEMO iodef.xml file
  (#1419)
* Removed approved status of ``sipr``, ``siflfwdrain`` and ``siflfwbot``
  mappings pending re-review (#1853)

Release 1.4.5, June 16, 2020
============================

* No changes.

Release 1.4.4, June 1, 2020
===========================

* No changes.

Release 1.4.3, May 12, 2020
===========================

* CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)

Release 1.4.2, April 30, 2020
=============================

* No changes.

Release 1.4.1, April 28, 2020
=============================

* No changes.

Release 1.4.0, April 23, 2020
=============================

* Added new approved mappings for sub-daily variables (#1704) ocean
  biogeochemistry (#1575), and FAFMIP (#1504).
* MIP Convert can now correctly produce sub-daily variables (#1577)

Release 1.3.4, March 27, 2020
=============================

* No changes.

Release 1.3.3, February 25, 2020
================================

* Processors using mask_copy routine do not now raise a TypeError referring
  to the numpy copyto() function (#1537)
* Corrected masking of polar row in data from CICE. Previously ORCA1 sea-ice
  data on T points and ORCA025 data on UV points was being masked incorrectly
  (#1624)

Release 1.3.2, January 27, 2020
===============================

* CRITICAL error messages from MIP Convert are correctly captured in the
  ``critical_issues.log`` file, and known exceptions from within MIP Convert
  will no longer lead to task failure in CDDS Convert suites (#1533).

Release 1.3.1, January 20, 2020
===============================

* Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* Added additional environmental variables setup in MIP Convert, and
  implemented cube rechunking to avoid performance issues when switching
  to Iris 2.2 (#1195)

Release 1.3.0, January 14, 2020
===============================

* Added processor to avoid ``ValueError`` when processing ``rsusLut`` (#889)
* A number of radiation and ocean biogeochemistry |model to MIP mappings| are
  now available (#1153)
* Added processor for ``vtem`` to mask data below 700 hPa (#1411)

Release 1.2.3, November 26, 2019
================================

* The variable ``wtem`` can now be produced (#875)
* The ``parent_activity_id`` global attribute in the |output netCDF files|
  is now correctly determined based on the ``parent_experiment_id`` (#1409)

Release 1.2.2, November 13, 2019
================================

* ``multiply_cubes`` processor for ``emibvoc`` and ``emiisop`` corrected to
  avoid "No data available for {year}; please check run_bounds" errors when
  processing more than one year of data at a time (#1343)

Release 1.2.1, October 29, 2019
===============================

* Correction of typo in mapping for ``wetoa`` (#1330)
* Approval of mappings for IPCC important variables ``rlutcs`` and ``rlutcsaf``
  (#1331)

Release 1.2.0, October 17, 2019
===============================

* ``This operation cannot be performed as there are differing coordinates
  remaining which cannot be ignored`` errors that occur when applying the
  |model to MIP mapping| expression have now been resolved due to the addition
  of a ``multiply_cubes`` processor (#275)
* Warnings related to ``invalid value encountered in divide`` are now not
  issued when processing |MIP requested variables| that use the
  ``divide_by_mask`` processor (#391)
* The duplication of constants in the ``original_name`` attribute in the
  |output netCDF files| (which described the |model to MIP mapping| expression)
  has now been removed (#1020)
* The ``parent_experiment_id`` must now be specified in the
  |user configuration file| whenever a parent exists (#1118)
* |MIP requested variables| on half levels (e.g. ``phalf``) can now be produced
  (#899)
* Implemented compatibility with the 01.00.31 version of the |MIP tables|
  (#1056)
* A number of |model to MIP mappings|, including carbon, cftables, cloud and
  land are now available (#990, #1016, #1257, #1259)
* The |model to MIP mappings| for ``drybc``, ``fgco2`` and ``evspsblsoi`` have
  now been corrected (#846, #1193, #1257)

Release 1.1.4, September 2, 2019
================================

* No changes.

Release 1.1.3, July 31, 2019
============================

* The |MIP requested variable name| is now written to the global attributes in
  the |output netCDF files| to help with identification (the ``out_name`` in
  the |MIP tables| sometimes differs from the |MIP requested variable name|;
  #1051)

Release 1.1.2, July 3, 2019
===========================

* No changes.

Release 1.1.1, June 27, 2019
============================

* No changes.

Release 1.1.0, June 12, 2019
============================

* MIP Convert now preferentially uses ``cftime``, falling back to using
  ``netcdftime`` if ``cftime`` is not available in the environment (#249)
* When replacing constants in the |model to MIP mapping| expressions, sometimes
  a constant would be replaced with the incorrect value when the constant has a
  name that shares the same root as the name of another constant; the constants
  are now replaced with the correct value and are explicitly written to the
  |output netCDF file| (#928)
* NEMO |MIP requested variables| on different grid points can now be produced
  in the same call to MIP Convert (#870)
* Multiple |model types| are now validated correctly against the values in the
  CVs (#904)
* Surface ocean biogeochemistry |MIP requested variables| can now be produced
  (#869)
* Pseudo zonal mean |MIP requested variables| can now be produced from NEMO
  ``diaptr`` files (#270)
* The production of MEDUSA ocean biogeochemistry |MIP requested variables| are
  now supported (#582)
* The issue related to data being set to zero due to integer division is now
  resolved (#861)
* A substantial number of |model to MIP mappings|, including carbon, land and
  ocean biogeochemistry, are now available (e.g. #759, #843, #853)

Release 1.0.5, May 10, 2019
===========================

* No changes.

Release 1.0.4, April 30, 2019
=============================

* No changes.

Release 1.0.3, April 5, 2019
============================

* No changes.

Release 1.0.2, April 5, 2019
============================

* No changes.

Release 1.0.1, April 2, 2019
============================

* Substreams can now be specified in the |user configuration files| (#198)
* A workaround was implemented to deal with the bug in ``iris.util.new_axis``,
  which causes the ``fill_value`` to be reset to the default value (#692)
* The polar rows in NEMO |model output files| are now masked prior to applying
  the |model to MIP mapping| expression (#702)
* The ``type`` parameter in the call to ``cmor.variable`` is now available
  (#715)
* The ``activity_id`` and ``source_type`` required global attributes are now
  validated by comparing their values to those in the CV file (#721)
* The version of the CV file is now recorded in the |output netCDF files|
  (#763)

Release 1.0.0, February 1, 2019
===============================

* First implementation of CDDS.
* Implemented compatibility with |CMOR| v3.4.0 and the 01.00.29 version of
  the |MIP tables|.
