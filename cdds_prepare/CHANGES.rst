.. (C) British Crown Copyright 2017-2022, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

Release 2.3.0, May 24, 2022
============================

* Development moved to github

Release 2.2.5, May 4, 2022
===========================

 * When inserting variables into CMIP6 processing the correct stream information is
   included (#2569)

Release 2.2.4, April 22, 2022
=============================

* No changes

Release 2.2.3, April 7, 2022
============================

* Reintroduce the capability to fall-back on default CMIP6 stream mappings when
  parsing user variable file (#2555)

Release 2.2.2, March 18, 2022
=============================

* Streams can now be set on creation of the requested variables file (#2498)

Release 2.2.1, February 15, 2022
================================

* No changes.

Release 2.2.0, February 9, 2022
===============================

* Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* Update to use python 3.8 (#2438)
* Enable the use of CDDS for ensemble class simulations (#2501, #2471)
* Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)

Release 2.1.2, November 25, 2021
================================

* No changes.

Release 2.1.1, October 26, 2021
===============================

* ``prepare_generate_variable_list`` can now generate requested variables  files using a user
   supplied list and the MIP tables being used, i.e. without reference to a  Data Request (#2358)

Release 2.1.0, September 6, 2021
================================

* The `--alternate_experiment_id` argument no longer triggers CRITICAL issues`
  (#2380)

Release 2.0.8, August 3, 2021
=============================

* No changes.

Release 2.0.7, July 15, 2021
============================

* No changes.

Release 2.0.6, June 29, 2021
============================

* Added functionality to ``prepare_generate_variable_list`` to automatically
  deactivate variables following a set of rules hosted in the CDDS repository
  (default) or in a text file. This "auto deactivation" can be skipped using
  the ``--no_auto_deactivation`` argument and the ``--auto_deactivation_file_name``
  option can be used to use a local file rather than the repository rules (#2405)

Release 2.0.5, June 11, 2021
============================

* No changes.

Release 2.0.4, May 17, 2021
===========================

* Allow for correct handling of packages where there are multiple mips / activity ids.
  The primary, i.e. first, mip will be used for all directory and dataset ids (#2369)
* Altered output of ``create_cdds_directory_structure`` to be a little more user
  friendly (#2369)

Release 2.0.3, April 28, 2021
=============================

* No changes.

Release 2.0.2, April 22, 2021
=============================

* No changes.

Release 2.0.1, March 25, 2021
=============================

* No changes.

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

* No changes.

Release 1.6.2, January 11, 2021
===============================

* No changes.

Release 1.6.1, November 26, 2020
================================

* No changes.

Release 1.6.0, November 05, 2020
================================

* As a default option, ``prepare_generate_variable_list`` now performs CMIP6 inventory
  check to determine which variables have already been produced, deactivating them
  automatically (#1899)
* Added requested ensemble size to the ``requested_variable_file`` file (#1900)
* The ``write_rose_suite_request_json`` script now correctly writes the name
  of the rose suite branch in the `request.json` file (#2001)
* All exceptions caught at the top script level are now logged as critical errors (#1968)

Release 1.5.5, October 20, 2020
===============================

* The requested variable list can now be constructed using an alternative
  ``experiment_id`` via a new command line argument to
  ``prepare_generate_variable_list``. This should only be used under advice
  from the CDDS team (#2057)

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

* No changes.

Release 1.5.0, July 2, 2020
===========================

* Added ``do-not-produce`` information to the requested variables file via a
  new ``producible`` attribute for each variable (#681)
* Added tool to export variable information from the requested
  variables file to a CSV or text file; ``create_variables_table_file`` (#1793)

Release 1.4.5, June 16, 2020
============================

* No changes.

Release 1.4.4, June 1, 2020
===========================

* No changes.

Release 1.4.3, May 12, 2020
===========================

* CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* Requested variable lists can now be generated using data request version
  ``01.00.32`` (#1800)

Release 1.4.2, April 30, 2020
=============================

* No changes.

Release 1.4.1, April 28, 2020
=============================

* No changes.

Release 1.4.0, April 23, 2020
=============================

* No changes.

Release 1.3.4, March 27, 2020
=============================

* ``prepare_alter_variable_list`` now includes additional variable metadata
  allowing ``cdds_store_spice`` to operate correctly for these variables
  (#1621)

Release 1.3.3, February 25, 2020
================================

* No changes.

Release 1.3.2, January 27, 2020
===============================

* No changes.

Release 1.3.1, January 20, 2020
===============================

* Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)

Release 1.3.0, January 14, 2020
===============================

* The new format of the approved variables file is now handled (#1175).
* Added ``EmonZ/sltbasin`` to the list of known good variables to avoid
  CRITICAL issue for UKESM1 processing (#1437)

Release 1.2.3, November 26, 2019
================================

* No changes.

Release 1.2.2, November 13, 2019
================================

* The ``create_cdds_directory_structure`` script now sets permissions on
  ``$CDDS_PROC_DIR/archive/log`` appropriately so users don't have to
  (#1347)

Release 1.2.1, October 29, 2019
===============================

* No changes.

Release 1.2.0, October 17, 2019
===============================

* The ``--root_config`` command line option for the
  ``create_cdds_directory_structure`` and ``prepare_generate_variable_list``
  scripts has now been removed (all arguments provided by the CDDS
  configuration files are now provided via command line options, see below;
  #1164)
* The ``--root_proc_dir`` and ``root_data_dir`` command line options for the
  ``create_cdds_directory_structure`` script have now been added (#1164)
* The ``--data_request_version``, ``--data_request_base_dir``,
  ``--mapping_status``, ``--root_proc_dir`` and ``root_data_dir`` command line
  options for the ``prepare_generate_variable_list`` script have now been added
  (#1164)
* Error ``RuntimeError: requested_variables targeted by rule 0 already active``
  or ``RuntimeError: requested_variables targeted by rule 0 already inactive``
  no longer occurs. Instead the comment describing the change will be added to
  the log and comments in the |requested variables list| and the
  |MIP requested variable| state will remain unchanged (#1210)
* Error ``ExperimentNotFoundError: Experiment name "<experiment identifier>"
  not found in this version of the data request`` no longer occurs when calling
  the ``prepare_generate_variable_list`` script when it is looking in the
  version of the |Data request| used for model configuration. Instead if the
  |experiment| is not defined in that version, a fallback |experiment| and the
  |MIP requested variables| associated with that |experiment| will be used for
  comparison with the current version of the data request (#1256)
* Additional |MIP Requested variables|, for which the description in the data
  request has changed between the versions used to configure the model and
  perform the processing, can now be produced (#1018)
* Ocean |MIP requested variables| that use |input variables| with constraints
  can now be produced (#995)

Release 1.1.4, September 2, 2019
================================

* No changes.

Release 1.1.3, July 31, 2019
============================

* No changes.

Release 1.1.2, July 3, 2019
===========================

* No changes.

Release 1.1.1, June 27, 2019
============================
* ``RFMIP`` is now included in the list of |MIPs| responded to by default when
  constructing |requested variables lists| (#994)

Release 1.1.0, June 12, 2019
============================

* |MIP requested variables| that do not exist in the version of the
  |data request| used to configure the |model| are now correctly accounted for
  when determining whether the |MIP requested variable| has changed
  significantly between the version of the |data request| used to setup the
  |model| and the specified version of the |data request| (#249)
* The list of |MIPs| that are included by default when constructing
  |requested variables lists| now includes ``PAMIP`` and ``CDRMIP`` (plus the
  correct spelling of ``AerChemMIP``) (#832)
* Ocean biogeochemistry field definitions from the model suites are now used
  when identifying |MIP requested variables| that can be produced (#820)

Release 1.0.5, May 10, 2019
===========================

* All |MIP requested variables| in the |requested variables list| can now be
  deactivated except those specified (which is useful for testing purposes)
  using the new ``prepare_select_variables`` script (#887)

Release 1.0.4, May 2, 2019
==========================

* No changes.

Release 1.0.3, April 18, 2019
=============================

* No changes.

Release 1.0.2, April 5, 2019
============================

* No changes.

Release 1.0.1, April 2, 2019
============================

* The significant changes between the |MIP requested variables| in the version
  of the |data request| used to setup HadGEM3 and version 01.00.29 of the
  |data request| were approved and added to ``KNOWN_GOOD_VARIABLES`` (#747)

Release 1.0.0, February 1, 2019
===============================

* First implementation of CDDS.
