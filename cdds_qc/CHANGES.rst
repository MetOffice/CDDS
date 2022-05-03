.. (C) British Crown Copyright 2018-2022, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

Release 2.2.4, April 22, 2022
=============================

* No changes

Release 2.2.3, April 7, 2022
============================

* Ignore QC errors caused by non-existant dimensions (#2548)

Release 2.2.2, March 18, 2022
=============================

* QC checks now refer to provided controlled vocabulary for non-CMIP6 projects (#2542)

Release 2.2.1, February 15, 2022
================================

* CF checks are now correctly filtered for CMIP6 data (#2531)

Release 2.2.0, February 9, 2022
===============================

* Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* Update to use python 3.8 (#2438)
* CDDS QC now uses the community version of IOOS/compliance-checker rather than a fork (#2381)
* Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* Fixed a bug where if the string `_concat` was used in the branch name two tests in `cdds_qc`
  would fail (#2521)

Release 2.1.2, November 25, 2021
================================

* No changes.

Release 2.1.1, October 26, 2021
===============================

* No changes.

Release 2.1.0, September 6, 2021
================================

* `qc_run_and_report` is now run as part of the conversion suite by `cdds_convert` by default
  (#1902, #2425, #2432)

Release 2.0.8, August 3, 2021
=============================

* No changes.

Release 2.0.7, July 15, 2021
============================

* No changes.

Release 2.0.6, June 29, 2021
============================

* No changes.

Release 2.0.5, June 11, 2021
===========================

* Floating point comparison will now not cause time contiguity checks to fail (#2396)

Release 2.0.4, May 17, 2021
===========================

* No changes.

Release 2.0.3, April 28, 2021
=============================

* No changes.

Release 2.0.2, April 22, 2021
=============================

* QC can now use a user specified directory with MIP tables provided by a command line option (#2331)

Release 2.0.1, March 25, 2021
=============================

* QC now correctly interprets the values within string coordinates, such as basin name (#2284)

Release 2.0, February 24, 2021
==============================

* Updated CDDS codebase to Python 3.6.

Release 1.6.5, February 22, 2021
================================

* Fixed a bug in diurnal cycle diagnostics checker (#2254).

Release 1.6.4, February 11, 2021
================================

* No changes.

Release 1.6.3, February 9, 2021
===============================

* Implemented support for diurnal cycle diagnostics (1hrCM frequency) (#1894)

Release 1.6.2, January 11, 2021
===============================

* No changes.

Release 1.6.1, November 26, 2020
================================

* No changes.

Release 1.6.0, November 05, 2020
================================

* All exceptions caught at the top script level are now logged as critical errors (#1968)

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

* No changes.

Release 1.5.0, July 2, 2020
===========================

* CDDS QC can now check CF sites (subhr frequency) data (#1783)

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

* CDDS QC can now check hourly frequency datasets and does not raise a
  ``KeyError`` exception (#1782)

Release 1.4.0, April 23, 2020
=============================

* Variables where a coordinate has text values, e.g. ``Omon/hfbasin``, can now
  be properly validated (#1456)
* Datasets at sub-daily frequencies can now be validated (#1578)
* ``CRITICAL`` failures are now logged for each dataset that fails a test
  (#1681)

Release 1.3.4, March 27, 2020
=============================

* QC has better support for processing a single stream using the ``--stream``
  command line option (#1622)

Release 1.3.3, February 25, 2020
================================

* No changes.

Release 1.3.2, January 27, 2020
===============================

* Implemented file size checker (#1530)

Release 1.3.1, January 20, 2020
===============================

* Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)

Release 1.3.0, January 14, 2020
================================

* A column with dataset filepaths has been added to the approved variables
  file (#1175)
* The quality checking can now be restricted to a single stream (#1248)
* CDDS QC now validates parent information when the ``branch_method`` is
  ``no parent`` (#1453)

Release 1.2.3, November 26, 2019
================================

* No changes.

Release 1.2.2, November 13, 2019
================================

* The data request version can now be overridden from the command line when
  running `qc_run_and_report` (#1375)

Release 1.2.1, October 29, 2019
===============================

* The validation of the CMIP6 license in |output netCDF files| now compares
  the ``license`` global attribute against the text provided in the
  ``request.json`` file (#1297)

Release 1.2.0, October 17, 2019
===============================

* The ``--root_config`` command line option for the ``qc_run_and_report``
  script has now been removed (all arguments provided by the CDDS configuration
  files are now provided via command line options, see below; #1167)
* The ``standard_names_dir``, ``controlled_vocabulary_dir``,
  ``--root_proc_dir`` and ``root_data_dir`` command line options for the
  ``qc_run_and_report`` script have now been added (#1167)

Release 1.1.4, September 2, 2019
================================

* No changes.

Release 1.1.3, July 31, 2019
============================

* Only the directory containing the |output netCDF files| are searched when
  looking for files to check (temporary files in other directories are ignored;
  (#1046)
* The |MIP requested variable name| rather than the name used in the filename
  (the ``out_name``) is now used when creating the approved list of
  |MIP requested variables| (#1052)

Release 1.1.2, July 3, 2019
===========================

* No changes.

Release 1.1.1, June 27, 2019
============================

* No changes.

Release 1.1.0, June 12, 2019
============================

* The start and end dates in the file name for each |MIP requested variable|
  are now validated against the |request| (#909)

Release 1.0.5, May 10, 2019
===========================

* No changes.

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

* The request JSON file is now a positional argument to ``qc_run_and_report``
  (#697)
* Single timestep |output netCDF files| are now handled appropriately (#769)
* Bound checks related to single depth levels are now ignored by default (the
  parameter ``--do_not_filter`` can be used to report these issues; #792)
* A detailed report can now be generated using the ``--details`` parameter
  (#793)
* An approved list of |MIP requested variables| can now be generated, which can
  be used to deactivate |MIP requested variables| in the
  |requested variables list| for the next round of processing (#819)

Release 1.0.0, February 1, 2019
===============================

* First implementation of CDDS.
