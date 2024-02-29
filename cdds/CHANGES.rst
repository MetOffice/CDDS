.. (C) British Crown Copyright 2017-2024, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

Release 2.5.8, February 29, 2024
================================
* Added submission queues to support CMIP6Plus publication (CDDSO-413)
* Removed modified time check from CDDS workflow to avoid workflow freezing when 
  moved to a different cylc server (CDDSO-405)

Release 2.5.7, February 21, 2024
================================
* Chunking of large moose queries in Extract is now correctly handled (CDDSO-398)
* QC now supports Conventions field in a more portable way (CDDSO-407)
* Concatenation code can now cope with monthly files of monthly mean
  data (CDDSO-405)
* Extensions and fixes to support CP4A processing via GCModel Dev (CDDSO-354,
  CDDSO-401, CDDSO-405)

Release 2.5.6, February 09, 2024
================================
* Added HadGEM3-GC5 and eUKESM1-1-ice model configurations to GCModelDev
  plugin (CDDSO-390, CDDSO-391)
* Extraction code now correctly handles coordinate variables when
  extracting data from NEMO diaptr and scalar files (CDDSO-394)
* The data version used in archiving can now be specified in the CDDS workflow
  to support additional runs of CDDS appending to the same data set (CDDSO-393)

Release 2.5.5, January 18, 2024
===============================
* The name of netCDF bounds coordinates variables are now configurable via
  plugins to support retrieval of NEMO4 ocean data (CDDSO-346)
* `GCModelDev` plugin now has an N96 GC3.05 generic model configuration and the
  list streams for the N216 equivalent has been extended (CDDSO-381)
* The option to overload model configuration via command line now correctly
  operates (CDDSO-376, CDDSO-379, CDDSO-380)
* The `create_variables_csv_file` script now also outputs the stream for each
  variable (CDDSO-332)

Release 2.5.4, December 13, 2023
================================
* Corrected an issue with a legacy configuration file that prevented the submission of CMIP6 data (CDDSO-371)
* Implement annual ocean diagnostics for the `GCOyr` MIP table (CDDSO-369)

Release 2.5.3, November 22, 2023
================================
* Adaptations needed for new CMIP6Plus MIP tables (CDDSO-336, CDDSO-365)
* Adaptations needed to support use of sub_experiment_ids that are not 
  “none” (CDDSO-365, CDDSO-362)
* Extract can again correctly retrieve sub-daily data (CDDSO-358)
* The update_directives script in the per-stream suite now correctly 
  calculate upper limits for memory / wall time / local storage (CDDSO-360)

Release 2.5.2, October 18, 2023
===============================
* Polar row masking is now specified directly in the MIP Convert config
  files (CDDSO-331)
* Memory, storage and time limits for SLURM jobs are now dynamically
  calculated after the first three cycles of the processing suite
  (CDDSO-212)
* CDDS can now handle hourly data files within a stream (CDDSO-349)
* The correct filenames for ocean data from ensemble suites are now
  used again (CDDSO-350)
* The CDDS suite uses a consistent calendar to the request, which
  ensures that concatenation processes, QC and archiving are correctly
  triggered (CDDSO-351)
* All options are now passed through to CDDS Convert by the CDDS
  processing workflow (CDDSO-348)

Release 2.5.1, August 4, 2023
=============================
* Ensure that recent versions of the NCO tools used for concatenation
  of files do not modify metadata, leading to publication issues (CDDSO-327)
* Fix creation_date validation bug in QC when data is written on the 31st
  of a month (CDDSO-326)

Release 2.5.0, July 27, 2023
============================
* Migrate CDDS to Cylc 8 (CDDSO-282, CDDSO-285, CDDSO-184)
* Introduce gregorian calendar support (CDDSO-231, CDDSO-235, CDDSO-240, CDDSO-244)
* Plugin and code development to support Regional models for projects such as CORDEX
  (CDDSO-233, CDDSO-68, CDDSO-74, CDDSO-261, CDDSO-149)
* CDDS now uses ISO datetime format for all time values in CDDS and MIP Convert config 
  files (CDDSO-313, CDDSO-45)
* Relocate test and etc directories to support alternate platforms and migration to 
  azure SPICE (CDDSO-131, CDDSO-273)
* Replace pep8 with pycodestyle (CDDSO-207)
* Separated extract validation into a separate script & task (CDDSO-243)
* Introduced retries to workflow tasks when submission fails (CDDSO-314)
* Amalgamated CDDS processing and ensemble processing workflows. Previous tools based 
  on u-cq805 and u-cr273 are deprecated (CDDSO-319)
* Updated CMOR to version 3.7.2, which required iris update to 3.4.1 (CDDSO-321)

Release 2.4.7, June 29, 2023
============================
* Fix a bug in the dehaloing script that prevented it from reading default command line
  arguments (CDDSO-308)

Release 2.4.6, June 23, 2023
============================
* Fix a bug in the extraction code where the non-uniform allocation of data in a simulation
  to a large number of tapes can lead to failure of cdds extract (CDDSO-245, CDDSO-289)
* Correct a bug in the HadGEM3 model config files that prevented extraction of data from the
  diaptr sub-stream in the NEMO ocean data for the GCModelDev project (CDSO-293)

Release 2.4.5, May 22, 2023
===========================
* Added HighResMIP models to CMIP6 plugin (CDDSO-158, cherry-picked from main)

Release 2.4.4, May 4, 2023
==========================
* Added options to use a “relaxed” approach to MIP name (activity_id), and experiment id, 
  that does not force checks from the CVs. This will allow users to process data as any 
  experiment id they like, but at the risk of typos due to the lack of checks against a 
  controlled vocabulary (CDDSO-253 , CDDSO-267, CDDSO-264) 
* `prepare_alter_variable_list` can now perform insert commands again as plugin was not 
  being loaded, which was needed for setting streams (CDDSO-269)
* `checkout_processing_suite`` now sets the streams in the suite based on  those in the 
  request file. (CDDSO-271)

Release 2.4.3, March 31, 2023
=============================

* Add support for retries in the run_extract task within the CDDS Convert Suite (CDDSO-258)

Release 2.4.2, March 1, 2023
============================

* Add support for filepaths with ensemble_id for netCDF model output (CDDSO-238).

Release 2.4.1, January 18, 2023
===============================

* Create a Cylc workflow for end to end processing (CDDSO-198, 200)
* Create a Cylc workflow for ensemble processing (CDDSO-199)
* Implement the `checkout_processing_suite` script for checking a copy of
  the CDDS Processing Suite (CDDSO-210)
* Create a Rose app for generating `request.json` files (CDDSO-3)
* Fix a bug where `cdds_convert` expect external plugins environmental variables to be set
  even if no plugin was used (CDDSO-216)

Release 2.4.0, September 12, 2022
=================================
* Refactoring of all CDDS packages into one package excluding MIP Convert (CDDSO-132, 133, 134, 135, 136,
  137, 138, 139, 140, 141, 142, 144)
* Move test execution from nose to pytest (CDDSO-128)
* Add sphinx docs (CDDSO-169)
* diaptr files for HadGEM3-GC31-MM can now be extracted from MASS (CDDSO-191)

Release 2.3.2, September 01, 2022
=================================
* (cdds_common): Default stream information for variables now held by Project level
  plugins (CDDSO-143)
* (cdds_configure): Log message issued when a stream cannot be found for a variable is now CRITICAL (CDDSO-178)
* (cdds_configure): GCAmon and GCLmon MIP tables from GCModelDev are now included in dictionary of default grids
  and will not be ignored  (CDDSO-178)
* (cdds_convert): Logger now set up before configure step is called allowing log information
  to be output (CDDSO-177)
* (cdds_convert): MIP Era now correctly propagated through to CDDS rose suite (CDDSO-180)
* (hadsdk): Change log message to CRITICAl for missing grid/stream.
* (hadsdk): Prepare a MIP convert branch to produce sample decadal data with additional
  seasonal forecasting metadata

Release 2.3.1, June 29, 2022
============================
* (cdds_common): Added auto-genereated table of CDDS variable mappings (CDDSO-120)
* (cdds_common): Fix inconsistency in case between mip era and plugin name (CDDSO-132)
* (extract): remove_ocean_haloes script now works after change to load plugin (CDDSO-152)

Release 2.3.0, May 24, 2022
===========================
* (cdds_common): Development moved to github
* (cdds_common): Version string now includes git commit hash (CDDSO-93)
* (cdds_configure): Development moved to github
* (cdds_convert): Development moved to github
* (cdds_prepare): Development moved to github
* (cdds_qc): Development moved to github
* (cdds_qc_plugin_cf17): Development moved to github
* (cdds_qc_plugin_cmip6): Development moved to github
* (cdds_transfer): Development moved to github
* (extract): Development moved to github
* (hadsdk): Development moved to github
* (transfer): Development moved to github

Release 2.2.5, May 4, 2022
==========================
* (cdds_common): The atmosphere timestep, used in some mappings, is now supplied via the
  ModelParameters class rather than a dictionary. This is only used for request
  JSON file creation (#2571)
* (cdds_configure): For non-CMIP6 projects the correct grid label and grid information is applied
  for variables where the grid is different to the default for that mip table (#2570)
* (cdds_prepare): When inserting variables into CMIP6 processing the correct stream information is
  included (#2569)
* (hadsdk): For non-CMIP6 projects the correct grid label and grid information is applied
  for variables where the grid is different to the default for that mip table (#2570)
* (hadsdk): The atmosphere timestep, used in some mappings, is now supplied via the
  ModelParameters class rather than a dictionary. This is only used for request
  JSON file creation (#2571)

Release 2.2.4, April 22, 2022
=============================
* (cdds_common): Added UKESM1-1-LL model to CMIP6 and GCModelDev projects (#2545)
* (transfer): Removed further calls to the moo test command when archiving data (#2559, #2560)

Release 2.2.3, April 7, 2022
============================
* (cdds_convert): The default cycling frequency will reduce to match the run bounds length when the run bounds
  length is smaller than cycling frequency. (#2006)
* (cdds_prepare): Reintroduce the capability to fall-back on default CMIP6 stream mappings when
  parsing user variable file (#2555)
* (cdds_qc): Ignore QC errors caused by non-existant dimensions (#2548)
* (cdds_qc_plugin_cf17): The implementation of the geographical region checker has been corrected (#2548)
* (extract): MASS paths with and without the ensemble_id in them are now handled (#2522)
* (transfer): moose listing commands are used rather than `moo test` in order to limit the number
  of commands talking to MASS, thereby limiting our vulnerability to transient or load
  dependent errors, and increases performance (#2553)

Release 2.2.2, March 18, 2022
=============================
* (cdds_common): Addition of GCModelDev plugin with core CMIP6 models (#2519)
* (cdds_prepare): Streams can now be set on creation of the requested variables file (#2498)
* (cdds_qc): QC checks now refer to provided controlled vocabulary for non-CMIP6 projects (#2542)
* (cdds_qc_plugin_cmip6): QC checks now refer to provided controlled vocabulary for non-CMIP6 projects (#2542)

Release 2.2.1, February 15, 2022
================================
* (cdds_common): UKESM1-ice-LL model information now loaded correctly (#2530)
* (cdds_convert): `--external_plugins` argument now passed through to all tasks (#2511)
* (cdds_qc): CF checks are now correctly filtered for CMIP6 data (#2531)
* (cdds_qc_plugin_cf17): CF checks are now correctly filtered for CMIP6 data (#2531)

Release 2.2.0, February 9, 2022
===============================
* (cdds_common): New module to take common code across CDDS and will ultimately replace hadsdk (#2460)
* (cdds_common): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (cdds_common): Update to use python 3.8 (#2438)
* (cdds_configure): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (cdds_configure): Update to use python 3.8 (#2438)
* (cdds_configure): Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* (cdds_convert): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (cdds_convert): Update to use python 3.8 (#2438)
* (cdds_convert): Enable the use of CDDS for ensemble class simulations (#2501, #2471)
* (cdds_convert): Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* (cdds_convert): When file concatenation is not required, i.e. when a single cycle covers the whole duration
  of the processing, files are now moved to the correct destination rather than being left in the
  `_concat` directory (#2521)
* (cdds_prepare): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (cdds_prepare): Update to use python 3.8 (#2438)
* (cdds_prepare): Enable the use of CDDS for ensemble class simulations (#2501, #2471)
* (cdds_prepare): Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* (cdds_qc): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (cdds_qc): Update to use python 3.8 (#2438)
* (cdds_qc): CDDS QC now uses the community version of IOOS/compliance-checker rather than a fork (#2381)
* (cdds_qc): Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* (cdds_qc): Fixed a bug where if the string `_concat` was used in the branch name two tests in `cdds_qc`
  would fail (#2521)
* (cdds_qc_plugin_cf17): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (cdds_qc_plugin_cf17): Update to use python 3.8 (#2438)
* (cdds_qc_plugin_cf17): CDDS QC now uses the community version of IOOS/compliance-checker rather than a fork (#2381)
* (cdds_qc_plugin_cf17): Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* (cdds_qc_plugin_cmip6): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (cdds_qc_plugin_cmip6): Update to use python 3.8 (#2438)
* (cdds_qc_plugin_cmip6): CDDS QC now uses the community version of IOOS/compliance-checker rather than a fork (#2381)
* (cdds_qc_plugin_cmip6): Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* (cdds_transfer): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (cdds_transfer): Update to use python 3.8 (#2438)
* (extract): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (extract): Update to use python 3.8 (#2438)
* (extract): Enable the use of CDDS for ensemble class simulations (#2501, #2471)
* (extract): Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* (hadsdk): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (hadsdk): Update to use python 3.8 (#2438)
* (hadsdk): Retired umfilelist and all connected code (#2438)
* (transfer): Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* (transfer): Update to use python 3.8 (#2438)

Release 2.1.2, November 25, 2021
================================
* (extract): Extract will now repeat creating stream directories if the first time fails because
  of intermittent filesystem issues (#2429)
* (hadsdk): Fixed an import bug in the ``mip_table_editor`` script (#2463)

Release 2.1.1, October 26, 2021
===============================
* (cdds_prepare): ``prepare_generate_variable_list`` can now generate requested variables  files using a user
  supplied list and the MIP tables being used, i.e. without reference to a  Data Request (#2358)
* (extract): Added the ``path_reformatter`` command line tool from the cdds_utils directory (#2415)
* (hadsdk): Improved error logging for the write_rose_suite_request_json script (#2390)
* (transfer): Added scripts for listing submission queues and resending stored messages that failed during submission
  (#2427, #2428)

Release 2.1.0, September 6, 2021
================================
* (cdds_configure): `generate_user_config_files` is now run by `cdds_convert` by default (#1902, #2425)
* (cdds_convert): The Extract, Configure, QC and archiving steps are now by default part of the conversion
  suite run by `cdds_convert` (#1902, #2383, #2425, #2432)
* (cdds_prepare): The `--alternate_experiment_id` argument no longer triggers CRITICAL issues`
  (#2380)
* (cdds_qc): `qc_run_and_report` is now run as part of the conversion suite by `cdds_convert` by default
  (#1902, #2425, #2432)
* (extract): `cdds_extract` is now run as part of the conversion suite by `cdds_convert` by default
  (#1902, #2425)
* (transfer): `cdds_store` is now run as part of the conversion suite by `cdds_convert` by default (#1902,
  #2425, #2432)
* (transfer): `cdds_sim_review` now handles per stream logs, qc reports and approved variables files
  (#1685)

Release 2.0.7, July 15, 2021
============================
* (extract): The ``remove_ocean_haloes`` command line tool is now available to remove halo rows and
  columns from ocean data files (#1161)

Release 2.0.6, June 29, 2021
============================
* (cdds_prepare): Added functionality to ``prepare_generate_variable_list`` to automatically
  deactivate variables following a set of rules hosted in the CDDS repository
  (default) or in a text file. This "auto deactivation" can be skipped using
  the ``--no_auto_deactivation`` argument and the ``--auto_deactivation_file_name``
  option can be used to use a local file rather than the repository rules (#2405)

Release 2.0.5, June 11, 2021
============================
* (cdds_qc): Floating point comparison will now not cause time contiguity checks to fail (#2396)

Release 2.0.4, May 17, 2021
===========================
* (cdds_prepare): Allow for correct handling of packages where there are multiple mips / activity ids.
  The primary, i.e. first, mip will be used for all directory and dataset ids (#2369)
* (cdds_prepare): Altered output of ``create_cdds_directory_structure`` to be a little more user
  friendly (#2369)
* (cdds_transfer): Allow for correct handling of packages where there are multiple mips / activity ids.
  The primary, i.e. first, mip will be used for all directory and dataset ids (#2369)
* (hadsdk): Allow for correct handling of packages where there are multiple mips / activity ids.
  The primary, i.e. first, mip will be used for all directory and dataset ids (#2369)
* (transfer): Allow for correct handling of packages where there are multiple mips / activity ids.
  The primary, i.e. first, mip will be used for all directory and dataset ids (#2369)

Release 2.0.3, April 28, 2021
=============================
* (transfer): CDDS store can now prepend files to an embargoed dataset provided the
  correct data version argument is provided (#2278)

Release 2.0.2, April 22, 2021
=============================
* (cdds_convert): Implemented changes necessary for conda deployment of CDDS code on JASMIN (#2240)
* (cdds_qc): QC can now use a user specified directory with MIP tables provided by a command line option (#2331)
* (hadsdk): Inventory can now be constructed or updated from CREPP database dump on JASMIN (#2148)
* (hadsdk): Corrected masking of polar rows for the ORCA12 grid (#2211)
* (hadsdk): Implemented changes necessary for conda deployment of CDDS code on JASMIN (#2240)

Release 2.0.1, March 25, 2021
=============================
* (cdds_qc): QC now correctly interprets the values within string coordinates, such as basin name (#2284)
* (extract): When running for a particular stream the stream name is now included in the
  log file name (#2014)
* (hadsdk): ``write_rose_suite_request_json`` can now create request files for the UKESM1-ice-LL
  model (#2264)
* (hadsdk): ``write_rose_suite_request_json`` now allows the `apt` stream (#2283)
* (transfer): CDDS store can now recover gracefully when continuing archiving following
  task failure due to issues with MASS (#2205)
* (transfer): CDDS store can now correctly handle pre-pending files to datasets and there are
  clearer error messages when issues arise (#2222)

Release 2.0.0, February 24, 2021
================================
* (cdds_configure): Updated CDDS codebase to Python 3.6.
* (cdds_convert): Updated CDDS codebase to Python 3.6.
* (cdds_prepare): Updated CDDS codebase to Python 3.6.
* (cdds_qc): Updated CDDS codebase to Python 3.6.
* (cdds_qc_plugin_cf17): Updated CDDS codebase to Python 3.6.
* (cdds_qc_plugin_cmip6): Updated CDDS codebase to Python 3.6.
* (cdds_transfer): Updated CDDS codebase to Python 3.6.
* (extract): Updated CDDS codebase to Python 3.6.
* (hadsdk): Updated CDDS codebase to Python 3.6.
* (transfer): Updated CDDS codebase to Python 3.6.

Release 1.6.5, February 22, 2021
================================
* (cdds_qc): Fixed a bug in diurnal cycle diagnostics checker (#2254).

Release 1.6.4, February 11, 2021
================================
* (hadsdk): ``write_rose_suite_request_json`` now correctly handles fields that are
  commented in the rose-suite.info file, an issue that affects the use of this
  script for amip-like  simulations in v1.6.3 (#2232)

Release 1.6.3, February 9, 2021
===============================
* (cdds_qc): Implemented support for diurnal cycle diagnostics (1hrCM frequency) (#1894)
* (hadsdk): Errors in rose suite metadata (rose-suite.info file) now cause
  write_rose_suite_request_json to fail rather than warn and branch
  dates are correctly handled (#1477)
* (hadsdk): Users can now override the start and end dates for processing when creating
  request files with write_rose_suite_request_json (#2212)
* (transfer): The failure of `moo put` commands is now handled more clearly (#2212)

Release 1.6.2, January 11, 2021
===============================
* (cdds_qc_plugin_cmip6): The ``cell_measures`` validation is now properly processing variables with ``--MODEL`` flag
  (#2193)

Release 1.6.1, November 26, 2020
================================
* (cdds_qc_plugin_cmip6): The ``cell_measures`` validation is now properly processing global averages (#2171)
* (extract): Fixed a bug in the validation report, where the expected number of files would be printed
  instead of the actual file count (#2174)

Release 1.6.0, November 05, 2020
================================
* (cdds_configure): All exceptions caught at the top script level are now logged as critical errors (#1968)
* (cdds_convert): All exceptions caught at the top script level are now logged as critical errors (#1968)
* (cdds_convert): Implemented code changes needed to support ARCHER filepath format and run CDDS on JASMIN (#2013)
* (cdds_convert): ``cdds_convert`` tasks now will fail if individual concatenation tasks do not succeed (#2045)
* (cdds_prepare): As a default option, ``prepare_generate_variable_list`` now performs CMIP6 inventory
  check to determine which variables have already been produced, deactivating them
  automatically (#1899)
* (cdds_prepare): Added requested ensemble size to the ``requested_variable_file`` file (#1900)
* (cdds_prepare): The ``write_rose_suite_request_json`` script now correctly writes the name
  of the rose suite branch in the `request.json` file (#2001)
* (cdds_prepare): All exceptions caught at the top script level are now logged as critical errors (#1968)
* (cdds_qc): All exceptions caught at the top script level are now logged as critical errors (#1968)
* (cdds_qc_plugin_cmip6): Consistency checks for ``netCDF`` variable attributes are now correctly applied (#2001)
* (cdds_qc_plugin_cmip6): Replaced the ``CMIP6`` ``Controlled Vocabulary`` tables with the ones bundled
  with ``CMOR`` (#1808)
* (cdds_transfer): All exceptions caught at the top script level are now logged as critical errors (#1968)
* (extract): All exceptions caught at the top script level are now logged as critical errors (#1968)
* (hadsdk): Implemented a new command line tool ``search_inventory`` for exploring
  archived datasets and checking their publication status (#1903)
* (hadsdk): Implemented code changes needed to support ARCHER filepath format
  and run CDDS on JASMIN (#2013)

Release 1.5.5, October 20, 2020
===============================
* (cdds_prepare): The requested variable list can now be constructed using an alternative
  ``experiment_id`` via a new command line argument to
  ``prepare_generate_variable_list``. This should only be used under advice
  from the CDDS team (#2057)
* (cdds_transfer): ``move_in_mass`` now correctly includes variables, where the
  |MIP requested variable name| and name used in the output file is different,
  when submitting data for publication (#2049).

Release 1.5.4, October 7, 2020
==============================
* (cdds_convert): Updated file sizing configuration for the high-resolution MM model now yields files under 20 Gb (#2037)

Release 1.5.3, September 16, 2020
=================================
* (cdds_convert): Increased memory limits, TMPDIR storage and changed cycling frequencies (#2012)

Release 1.5.2, September 4, 2020
================================
* (cdds_qc_plugin_cmip6): Fixed a bug that prevented from validation of some global attributes of
  simulations without a parent experiment (#2000)

Release 1.5.1, August 20, 2020
==============================
* (cdds_convert): The concatenation processes should no longer leave temporary netCDF files
  behind when the batch job hits its wall time (#1895)
* (cdds_convert): The check on the use of TMPDIR storage in the MIP Convert tasks is now
  correctly applied (#1943)
* (cdds_convert): The cycling frequencies for the conversion process can now been overridden
  from the command line (#1944)
* (extract): Information on the validation of the is now written to <stream>_validation.txt
  as well as to the log files (#1811)
* (transfer): cdds_store can now archive CF sites datawith frequency subhrPt (#1945)
* (transfer): cdds_store will now raise CRITICAL log messages, rather than ERROR when
  something goes wrong (#1934)

Release 1.5.0, July 2, 2020
===========================
* (cdds_configure): Settings and files needed for production of CF sites data are now
  correctly written to the MIP Convert template files (#1838)
* (cdds_convert): CDDS can now produce CF Sites data (#1838)
* (cdds_prepare): Added ``do-not-produce`` information to the requested variables file via a
  new ``producible`` attribute for each variable (#681)
* (cdds_prepare): Added tool to export variable information from the requested
  variables file to a CSV or text file; ``create_variables_table_file`` (#1793)
* (cdds_qc): CDDS QC can now check CF sites (subhr frequency) data (#1783)
* (extract): CDDS Extract now correctly reports failure through error codes and e-mails
  (#1807)
* (extract): CDDS Extract can now correctly retrieve daily MEDUSA data (#1803)

Release 1.4.5, June 16, 2020
============================
* (hadsdk): Institution names and branching dates are now correctly processed and
  written by the ``write_rose_suite_request_json`` script (#1848, #1849)

Release 1.4.4, June 1, 2020
===========================
* (cdds_convert): Memory limits for ``ap4`` stream have been extended to 12G to avoid task
  failure (#1843)
* (cdds_convert): The copying of files to ``$TMPDIR`` will now be retried twice and if all
  attempts fail the task will fail rather than allowing CRITICAL errors from
  MIP Convert (#1839)

Release 1.4.3, May 12, 2020
===========================
* (cdds_convert): CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* (cdds_convert): Added ``--scale-memory-limits`` argument to CDDS Convert to allow memory limits
  to be altered at run time if necessary (#1806)
* (cdds_prepare): CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* (cdds_prepare): Requested variable lists can now be generated using data request version
  ``01.00.32`` (#1800)
* (cdds_qc): CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* (cdds_qc_plugin_cf17): CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* (cdds_qc_plugin_cmip6): CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* (cdds_transfer): CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* (extract): CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* (hadsdk): CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* (hadsdk): Added ``write_rose_suite_request_json`` to construct a request JSON file
  from the rose-suite.info file within a CMIP6 suite (#1732)
* (transfer): CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)

Release 1.4.2, April 30, 2020
=============================
* (cdds_qc_plugin_cmip6): CDDS QC now handles variables where the ``cell_measures`` variable attribute
  is optional (#1801)
* (hadsdk): ``write_request_json`` now gives a useful error message when
  there is inconsistent data in CREM for a package (#1765)

Release 1.4.1, April 28, 2020
=============================
* (cdds_convert): CDDS Convert now does not raise an ``AttributeError`` relating to the
  ``--email-notifications`` argument when run (#1780)
* (cdds_qc): CDDS QC can now check hourly frequency datasets and does not raise a
  ``KeyError`` exception (#1782)

Release 1.4.0, April 23, 2020
=============================
* (cdds_convert): Sub-daily data can now be produced (#825, #1577, #1704)
* (cdds_convert): The memory requested for different tasks within the suites is now controlled
  on a per grid/stream basis (#941, #1474)
* (cdds_convert): E-mail alerts now issued by suites launched by CDDS Convert when completing
  or stalling (#1669)
* (cdds_qc): Variables where a coordinate has text values, e.g. ``Omon/hfbasin``, can now
  be properly validated (#1456)
* (cdds_qc): Datasets at sub-daily frequencies can now be validated (#1578)
* (cdds_qc): ``CRITICAL`` failures are now logged for each dataset that fails a test
  (#1681)
* (extract): Extract can now extract data from sub-daily PP streams (#359)
* (extract): Extract processes for individual streams can now be run in separate tasks
  (#1619)
* (hadsdk): When writing request JSON files from CREM, warnings are issued if
  base dates are not ``1850-01-01`` (#1703)

Release 1.3.4, March 27, 2020
=============================
* (cdds_prepare): ``prepare_alter_variable_list`` now includes additional variable metadata
  allowing ``cdds_store_spice`` to operate correctly for these variables (#1621)
* (cdds_qc): QC has better support for processing a single stream using the ``--stream``
  command line option (#1622)
* (cdds_transfer): ``move_in_mass`` now only lists directories in MASS connected with
  the Request provided, significantly reducing run time (#1649).
* (transfer): Errors arising from MOO failures are now properly handled and logged (#1701)
* (transfer): Transfer now supports processing variables with different output names to
  their variable ID, and has better support for processing a single stream
  using the --stream command line option (#1622)

Release 1.3.3, February 25, 2020
================================
* (cdds_convert): ``cdds_convert`` script now correctly returns a non-zero error code on error
  (#1501).
* (cdds_convert): The conversion process can now be limited to specified streams
  via the ``--streams`` command line argument (#1594)
* (cdds_convert): The conditions under which an ``organise_files_final`` task have been
  modified to avoid scheduling duplicate file management processes (#1585)
* (extract): Extract will no longer log CRITICAL errors when processing data
  streams containing no retrievable variables (#1583, #1354).

Release 1.3.2, January 27, 2020
===============================
* (cdds_convert): CRITICAL error messages from MIP Convert are correctly captured in the
  ``critical_issues.log`` file, and known exceptions from within MIP Convert
  will no longer lead to task failure in CDDS Convert suites (#1533).
* (cdds_qc): Implemented file size checker (#1530)
* (extract): Clarified CRITICAL messages when PP files are found to be incomplete
  (#1528)
* (extract): Extract does not now raise an error when attempting to interpret the
  request file for ``HadGEM3-GC31-MM`` packages (#1563)
* (transfer): ``cdds_store`` now handles experiment ids including the ``-`` character
  (#1556)

Release 1.3.1, January 20, 2020
===============================
* (cdds_configure): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (cdds_convert): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (cdds_prepare): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (cdds_qc): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (cdds_qc_plugin_cf17): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (cdds_qc_plugin_cmip6): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (cdds_transfer): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (extract): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (hadsdk): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (transfer): Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* (transfer): ``cdds_store_spice`` now passes all arguments through to spice job (#1511)
* (transfer): ``cdds_store`` behaves correctly when there are no files to archive (#1520)

Release 1.3.0, January 14, 2020
===============================
* (cdds_prepare): The new format of the approved variables file is now handled (#1175).
* (cdds_prepare): Added ``EmonZ/sltbasin`` to the list of known good variables to avoid
  CRITICAL issue for UKESM1 processing (#1437)
* (cdds_qc): A column with dataset filepaths has been added to the approved variables
  file (#1175)
* (cdds_qc): The quality checking can now be restricted to a single stream (#1248)
* (cdds_qc): CDDS QC now validates parent information when the ``branch_method`` is
  ``no parent`` (#1453)
* (cdds_transfer): The new format of the approved variables file is now handled (#1175).
* (cdds_transfer): Added new archiving tool ``cdds_store`` to replace ``send_to_mass`` and
  ``cdds_transfer_spice`` (#1384)
* (extract): CDDS Extract no longer connects to CREM to retrieve request information
  (#1079, #1080).
* (extract): ``--root_proc_dir`` and ``--root_data_dir`` arguments are now correctly
  interpreted by the ``cdds_extract_spice`` command (#1478).
* (extract): Error messages related to unreadable pp files are now being correctly
  logged (#1154).
* (transfer): Added new archiving tool ``cdds_store`` to replace ``send_to_mass`` and
  ``cdds_transfer_spice`` (#1384)

Release 1.2.3, November 26, 2019
================================
* (hadsdk): ``thetaot`` and ``sltbasin`` can now be produced after correcting their
  stream (#1009)

Release 1.2.2, November 13, 2019
================================
* (cdds_prepare): The ``create_cdds_directory_structure`` script now sets permissions on
  ``$CDDS_PROC_DIR/archive/log`` appropriately so users don't have to
  (#1347)
* (cdds_qc): The data request version can now be overridden from the command line when
  running `qc_run_and_report` (#1375)
* (cdds_transfer): The failure to submit a RabbitMQ message, which triggers the publication
  process, is now accompanied by a critical log message (#1346)
* (extract): CDDS Extract will now log WARNING rather than CRITICAL messages when there
  are no variables to be extracted for a stream (#1354)
* (extract): All moose commands are now non-resumable, in order to avoid cases where MASS
  outages lead to conflicts with CDDS Extract processes (#1374)

Release 1.2.1, October 29, 2019
===============================
* (cdds_convert): The ``cdds_convert.log`` file is now written to the ``convert/log``
  processing directory rather than the working directory (as seen at v1.2.0)
  (#1341)
* (cdds_convert): CDDS Convert now ignores streams where there are no |MIP requested variables|
  to be processed rather than raising a ``KeyError`` (#1282)
* (cdds_qc): The validation of the CMIP6 license in |output netCDF files| now compares
  the ``license`` global attribute against the text provided in the
  ``request.json`` file (#1297)
* (extract): A bug in the |netCDF| validation process, introduced in v1.2.0, that
  resulted in all NEMO model output files being incorrectly identified as
  unreadable, and then deleted, has been fixed (#1333)

Release 1.2.1, October 28, 2019
===============================
* (hadsdk): PP header fixes are now correctly applied when producing information
  required to construct query files for ``moo select`` commands in CDDS
  Extract.  This enables the correct extraction of data for ``clisccp``
  (#1330)

Release 1.2.0, October 17, 2019
===============================
* (cdds_configure): The ``cdds_configure`` script is now called ``generate_user_config_files``
  (#1043)
* (cdds_configure): The ``--mohc`` and ``--root_config`` command line options for the
  ``generate_user_config_files`` script have now been removed (all arguments
  provided by the CDDS configuration files are now provided via command line
  options, see below; #1043)
* (cdds_configure): The ``--data_request_version``, ``--template_name``, ``--root_proc_dir`` and
  ``root_data_dir`` command line options for the ``generate_user_config_files``
  script have now been added (#1043, #1070)
* (cdds_convert): The ``--root_config`` command line option for the ``cdds_convert`` script has
  now been removed (all arguments provided by the CDDS configuration files are
  now provided via command line options, see below; #1070)
* (cdds_convert): The ``--root_proc_dir`` and ``root_data_dir`` command line options for the
  ``cdds_convert`` script have now been added (#1070)
* (cdds_prepare): The ``--root_config`` command line option for the
  ``create_cdds_directory_structure`` and ``prepare_generate_variable_list``
  scripts has now been removed (all arguments provided by the CDDS
  configuration files are now provided via command line options, see below;
  #1164)
* (cdds_prepare): The ``--root_proc_dir`` and ``root_data_dir`` command line options for the
  ``create_cdds_directory_structure`` script have now been added (#1164)
* (cdds_prepare): The ``--data_request_version``, ``--data_request_base_dir``,
  ``--mapping_status``, ``--root_proc_dir`` and ``root_data_dir`` command line
  options for the ``prepare_generate_variable_list`` script have now been added
  (#1164)
* (cdds_prepare): Error ``RuntimeError: requested_variables targeted by rule 0 already active``
  or ``RuntimeError: requested_variables targeted by rule 0 already inactive``
  no longer occurs. Instead the comment describing the change will be added to
  the log and comments in the |requested variables list| and the
  |MIP requested variable| state will remain unchanged (#1210)
* (cdds_prepare): Error ``ExperimentNotFoundError: Experiment name "<experiment identifier>"
  not found in this version of the data request`` no longer occurs when calling
  the ``prepare_generate_variable_list`` script when it is looking in the
  version of the |Data request| used for model configuration. Instead if the
  |experiment| is not defined in that version, a fallback |experiment| and the
  |MIP requested variables| associated with that |experiment| will be used for
  comparison with the current version of the data request (#1256)
* (cdds_prepare): Additional |MIP Requested variables|, for which the description in the data
  request has changed between the versions used to configure the model and
  perform the processing, can now be produced (#1018)
* (cdds_prepare): Ocean |MIP requested variables| that use |input variables| with constraints
  can now be produced (#995)
* (cdds_qc): The ``--root_config`` command line option for the ``qc_run_and_report``
  script has now been removed (all arguments provided by the CDDS configuration
  files are now provided via command line options, see below; #1167)
* (cdds_qc): The ``standard_names_dir``, ``controlled_vocabulary_dir``,
  ``--root_proc_dir`` and ``root_data_dir`` command line options for the
  ``qc_run_and_report`` script have now been added (#1167)
* (cdds_qc_plugin_cmip6): CDDS QC now confirms that the ``parent_experiment_id`` attribute in
  the |output netCDF files| is consistent with the ``Request`` and
  |Controlled Vocabulary|, allowing for the choice of ``parent_experiment_id``
  where there are options within the |Controlled vocabulary| (#1083)
* (cdds_transfer): The ``send_to_mass`` and ``cdds_transfer_spice`` scripts now raise critical
  log messages rather than error log messages, where appropriate (#1045)
* (extract): CDDS Extract now handles ``TSSC_SPANS_TOO_MANY_RESOURCES`` errors raised by
  ``moo`` commands that attempt to access files on too many tapes (#814)
* (hadsdk): The ``mip_era`` and ``--root_config`` command line options for the
  ``write_request_json`` script have now been removed (all arguments provided
  by the CDDS configuration files are now provided via command line options;
  #1078)
* (hadsdk): The ``--root_config`` command line option for the
  ``check_request_json_against_crem`` script has now been removed (all
  arguments provided by the CDDS configuration files are now provided via
  command line options; #1078)
* (hadsdk): The value of the ``parent_time_units`` attribute can now be interpreted by
  ``cf_units`` (#1220)
* (hadsdk): The ``write_request_json`` script now writes the ``parent_experiment_id`` to
  the request JSON file (#1109)

Release 1.1.4, September 2, 2019
================================
* (cdds_convert): To avoid causing storage issues on SPICE the MIP Convert tasks in the CDDS
  Convert Rose suites now report the local disk usage (if suite variable
  $STAGING_DIR is set). If this limit is specified then tasks that exceed the
  limit will fail (#1158).
* (cdds_convert): To enable HadGEM3-GC31-MM (N216) processing the requests for local temporary
  storage ($TMPDIR), in the MIP Convert tasks within the Rose suites, have
  been extended (#1158).
* (extract): When validating |netCDF| model output files, Extract now identifies faulty
  files with no time records (#992).
* (hadsdk): ``Experiment name not found in this version of the data request`` errors in
  ``prepare_generate_variable_list``, which occurred for some |experiments| in
  HadGEM3, have been resolved (#1189)

Release 1.1.3, July 31, 2019
============================
* (cdds_qc): Only the directory containing the |output netCDF files| are searched when
  looking for files to check (temporary files in other directories are ignored;
  (#1046)
* (cdds_qc): The |MIP requested variable name| rather than the name used in the filename
  (the ``out_name``) is now used when creating the approved list of
  |MIP requested variables| (#1052)
* (cdds_transfer): To ensure messages sent to CEDA when withdrawing data contain the correct
  version date stamp, the version date stamp used in the path in MASS now
  doesn't change during state changes (#919)
* (extract): To avoid issues related to extracting a large number of netCDF
  |model output files| from MASS, the extraction is now performed in multiple
  chunks (#991)

Release 1.1.2, July 3, 2019
===========================
* (cdds_convert): Following updates to the MIP Concatenate sizing file to ensure that
  |output netCDF files| containing daily output on model levels are now
  correctly sized (#1002)
* (hadsdk): Ocean ancillary variables are now correctly recognised in several
  |model to MIP mapping| expressions (#944)

Release 1.1.1, June 27, 2019
============================
* (cdds_prepare): ``RFMIP`` is now included in the list of |MIPs| responded to by default when
  constructing |requested variables lists| (#994)
* (cdds_qc_plugin_cmip6): Fixed a bug in CF Standard Names parser that prevented validation of
  `Emon/ta` (#993).
* (extract): Faulty |model output files| are now removed when issues are identified (#918).

Release 1.1.0, June 12, 2019
============================
* (cdds_convert): CDDS Convert now preferentially uses ``cftime``, falling back to using
  ``netcdftime`` if ``cftime`` is not available in the environment (#249)
* (cdds_convert): A temporary local storage allocation is now requested in SPICE job scripts
  in order to avoid job failures due to lack of disk space (#824) and the
  settings controlling the temporal extent of the output files has been
  updated to include daily IPCC critical variables (#824, #883, #921)
* (cdds_convert): |MIP requested variables| can now be processed from the ``apm`` |stream|
  (#922)
* (cdds_prepare): |MIP requested variables| that do not exist in the version of the
  |data request| used to configure the |model| are now correctly accounted for
  when determining whether the |MIP requested variable| has changed
  significantly between the version of the |data request| used to setup the
  |model| and the specified version of the |data request| (#249)
* (cdds_prepare): The list of |MIPs| that are included by default when constructing
  |requested variables lists| now includes ``PAMIP`` and ``CDRMIP`` (plus the
  correct spelling of ``AerChemMIP``) (#832)
* (cdds_prepare): Ocean biogeochemistry field definitions from the model suites are now used
  when identifying |MIP requested variables| that can be produced (#820)
* (cdds_qc): The start and end dates in the file name for each |MIP requested variable|
  are now validated against the |request| (#909)
* (cdds_qc_plugin_cmip6): The CMIP6 Compliance Checker Plugin now preferentially uses ``cftime``,
  falling back to using ``netcdftime`` if ``cftime`` is not available in the
  environment (#249)
* (extract): Daily ocean data can now be extracted from MASS (#882)
* (extract): Extract logs now contain the CRITICAL keyword for critical issues (#903)
* (extract): ``Exceeded step memory limit`` errors in ``cdds_extract_spice`` have been
  resolved (#915)
* (extract): The production of MEDUSA ocean biogeochemistry |MIP requested variables| are
  now supported (#582)
* (hadsdk): ``Exceeded step memory limit`` errors in ``cdds_extract_spice`` have been
  resolved (#915)
* (hadsdk): The production of MEDUSA ocean biogeochemistry |MIP requested variables| are
  now supported (#582)
* (hadsdk): HadSDK now preferentially uses ``cftime``, falling back to using
  ``netcdftime`` if ``cftime`` is not available in the environment (#249)

Release 1.0.5, May 10, 2019
===========================
* (cdds_prepare): All |MIP requested variables| in the |requested variables list| can now be
  deactivated except those specified (which is useful for testing purposes)
  using the new ``prepare_select_variables`` script (#887)

Release 1.0.4, May 2, 2019
==========================
* (cdds_configure): MIP Convert template files for the ocean are now produced separately for each
  sub-stream to avoid an issue where ocean files _may_ be produced with
  incorrect spatial coordinates (#871). This change also improves CDDS Convert
  end-to-end performance by splitting processing into several smaller batch
  jobs that can be run in parallel.
* (cdds_convert): Candidate concatenation file is now written to an intermediate directory, so
  that temporary files do not land up in the output directory and then in the
  publication pipeline (#849)
* (cdds_convert): Fixed a bug where after a timeout, a concatenation task would not produce
  all the expected output (#849)
* (cdds_transfer): Added command line option to ``move_in_mass`` script to allow state changes,
  such as ``embargoed`` to ``available`` or ``available`` to ``withdrawn``, to
  be limited to a list of variables (#876)

Release 1.0.4, April 30, 2019
=============================
* (cdds_qc_plugin_cmip6): The validation of the ``activity_id`` global attribute in
  |output netCDF files|, as written by |CMOR|, now allows for multiple |MIPs|
  to be specified in the CMIP6 |Controlled Vocabulary| for a particular
  |experiment|. For example, data produced for |experiment| ``ssp370`` should
  have an ``activity_id`` of ``ScenarioMIP AerChemMIP`` (#865)
* (extract): Some unit test utility functions were moved from extract to hadsdk (#865).
* (hadsdk): Some unit test utility functions were moved from extract to hadsdk (#865)

Release 1.0.3, April 18, 2019
=============================
* (cdds_convert): Mip_convert and mip_concatenate now write to three separate directories: one
  for mip_convert output, a second for input files to the concatenation tasks
  and a third for the final concatenation tasks which is where qc and transfer
  will look for the output (#840)
* (cdds_convert): Updated the calculation of the concatenation task cycle time for suites that
  only have 1 scheduled concatenation task due to the short run time (#852)
* (cdds_transfer): The MOOSE ``command-id`` is now reported via ``run_moo_cmd`` to allow CEDA's
  CREPP tools to kill processes left running on the MOOSE controllers that
  should have ended when the command line MOOSE client exited (#855)

Release 1.0.2, April 5, 2019
============================
* (hadsdk): The ``hadsdk.common.netCDF_regexp()`` function now returns a regular
  expression that contains 4 match groups, allowing the extraction of NEMO
  |model output files| (#834)

Release 1.0.1, April 2, 2019
============================
* (cdds_configure): The grid label ``gn`` is now used for datasets that use |model output files|
  on all T/U/V/UV grids (#761)
* (cdds_convert): The |stream identifiers| and grid identifiers are now obtained directly from
  the |user configuration files| (#555)
* (cdds_convert): One Rose suite per |stream identifier| is now submitted rather than one Rose
  suite per request (#710)
* (cdds_convert): The argument provided to the ``--rose-suite-branch`` parameter can now be a
  path to a checked out version of the Rose suite (for development purposes
  only; #739)
* (cdds_convert): The Rose suite now removes directories where outputs are written prior to
  producing those outputs (#750)
* (cdds_convert): The concatenation periods are now aligned with the reference date (#762)
* (cdds_convert): A single |output netCDF file| is now produced if the concatenation period is
  more than the run bounds (#778)
* (cdds_convert): The correct files are now included in each concatenation period (#780)
* (cdds_convert): The cycles to run MIP Convert are now aligned with the reference date (#781)
* (cdds_prepare): The significant changes between the |MIP requested variables| in the version
  of the |data request| used to setup HadGEM3 and version 01.00.29 of the
  |data request| were approved and added to ``KNOWN_GOOD_VARIABLES`` (#747)
* (cdds_qc): The request JSON file is now a positional argument to ``qc_run_and_report``
  (#697)
* (cdds_qc): Single timestep |output netCDF files| are now handled appropriately (#769)
* (cdds_qc): Bound checks related to single depth levels are now ignored by default (the
  parameter ``--do_not_filter`` can be used to report these issues; #792)
* (cdds_qc): A detailed report can now be generated using the ``--details`` parameter
  (#793)
* (cdds_qc): An approved list of |MIP requested variables| can now be generated, which can
  be used to deactivate |MIP requested variables| in the
  |requested variables list| for the next round of processing (#819)
* (cdds_transfer): The new command line script ``cdds_transfer_spice`` can now be used to run
  CDDS Transfer on SPICE (#688)
* (cdds_transfer): The name of the directory used to store |output netCDF files| on MASS can now
  be specified via the ``--mass_location`` parameter (#756)
* (cdds_transfer): The SPICE logs for ``cdds_transfer_spice`` are now written to the correct
  location when using the ``--use_proc_dir`` parameter (#828)
* (extract): A workaround was implemented to deal with the fact that the ``moo ls``
  command sometimes returns a truncated list of filenames (#771)
* (hadsdk): The ``write_request_json`` script now works correctly for experiments without
  parents, and retrieves the correct value of the |model type| from CREM (#730)

Release 1.0.0, February 1, 2019
===============================
* (cdds_configure): First implementation of CDDS.
* (cdds_convert): First implementation of CDDS.
* (cdds_prepare): First implementation of CDDS.
* (cdds_qc): First implementation of CDDS.
* (cdds_qc_plugin_cf17): First implementation of CDDS.
* (cdds_qc_plugin_cmip6): First implementation of CDDS.
* (cdds_transfer): First implementation of CDDS.
* (extract): First implementation of CDDS.
* (hadsdk): First implementation of CDDS.
* (transfer): First implementation of CDDS.

