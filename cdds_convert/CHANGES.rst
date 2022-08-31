.. (C) British Crown Copyright 2017-2022, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

Release 2.3.2, September 01, 2022
=================================

* Logger now set up before configure step is called allowing log information
  to be output (CDDSO-177)
* MIP Era now correctly propagated through to CDDS rose suite (CDDSO-180)

Release 2.3.1, June 29, 2022
============================

* No changes.

Release 2.3.0, May 24, 2022
============================

* Development moved to github

Release 2.2.5, May 4, 2022
============================

* No changes

Release 2.2.4, April 22, 2022
=============================

* No changes

Release 2.2.3, April 7, 2022
============================

* The default cycling frequency will reduce to match the run bounds length when the run bounds
  length is smaller than cycling frequency. (#2006)

Release 2.2.2, March 18, 2022
=============================

* No changes.

Release 2.2.1, February 15, 2022
================================

* `--external_plugins` argument now passed through to all tasks (#2511)

Release 2.2.0, February 9, 2022
===============================

* Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* Update to use python 3.8 (#2438)
* Enable the use of CDDS for ensemble class simulations (#2501, #2471)
* Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)
* When file concatenation is not required, i.e. when a single cycle covers the whole duration
  of the processing, files are now moved to the correct destination rather than being left in the
  `_concat` directory (#2521)

Release 2.1.2, November 25, 2021
================================

* No changes.

Release 2.1.1, October 26, 2021
===============================

* No changes.

Release 2.1.0, September 6, 2021
================================

* The Extract, Configure, QC and archiving steps are now by default part of the conversion
  suite run by `cdds_convert` (#1902, #2383, #2425, #2432)

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
============================

* No changes.

Release 2.0.4, May 17, 2021
===========================

* No changes.

Release 2.0.3, April 28, 2021
=============================

* No changes.

Release 2.0.2, April 22, 2021
=============================

* Implemented changes necessary for conda deployment of CDDS code on JASMIN (#2240)

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

* All exceptions caught at the top script level are now logged as critical errors (#1968)
* Implemented code changes needed to support ARCHER filepath format and run CDDS on JASMIN (#2013)
* ``cdds_convert`` tasks now will fail if individual concatenation tasks do not succeed (#2045)

Release 1.5.5, October 20, 2020
===============================

* No changes.

Release 1.5.4, October 7, 2020
==============================

* Updated file sizing configuration for the high-resolution MM model now yields files under 20 Gb (#2037)

Release 1.5.3, September 16, 2020
=================================

* Increased memory limits, TMPDIR storage and changed cycling frequencies (#2012)

Release 1.5.2, September 4, 2020
================================

* No changes.

Release 1.5.1, August 20, 2020
==============================

* The concatenation processes should no longer leave temporary netCDF files
  behind when the batch job hits its wall time (#1895)
* The check on the use of TMPDIR storage in the MIP Convert tasks is now
  correctly applied (#1943)
* The cycling frequencies for the conversion process can now been overridden
  from the command line (#1944)

Release 1.5.0, July 2, 2020
===========================

 * CDDS can now produce CF Sites data (#1838)

Release 1.4.5, June 16, 2020
============================

* No changes.

Release 1.4.4, June 1, 2020
===========================

* Memory limits for ``ap4`` stream have been extended to 12G to avoid task
  failure (#1843)
* The copying of files to ``$TMPDIR`` will now be retried twice and if all
  attempts fail the task will fail rather than allowing CRITICAL errors from
  MIP Convert (#1839)

Release 1.4.3, May 12, 2020
===========================

* CDDS can now process data for the model ``UKESM1-ice-LL`` (#1513)
* Added ``--scale-memory-limits`` argument to CDDS Convert to allow memory limits
  to be altered at run time if necessary (#1806)

Release 1.4.2, April 30, 2020
=============================

* No changes.

Release 1.4.1, April 28, 2020
=============================

* CDDS Convert now does not raise an ``AttributeError`` relating to the
  ``--email-notifications`` argument when run (#1780)

Release 1.4.0, April 23, 2020
=============================

* Sub-daily data can now be produced (#825, #1577, #1704)
* The memory requested for different tasks within the suites is now controlled
  on a per grid/stream basis (#941, #1474)
* E-mail alerts now issued by suites launched by CDDS Convert when completing
  or stalling (#1669)

Release 1.3.4, March 27, 2020
=============================

* No changes

Release 1.3.3, February 25, 2020
================================

* ``cdds_convert`` script now correctly returns a non-zero error code on error
  (#1501).
* The conversion process can now be limited to specified streams
  via the ``--streams`` command line argument (#1594)
* The conditions under which an ``organise_files_final`` task have been
  modified to avoid scheduling duplicate file management processes (#1585)

Release 1.3.2, January 27, 2020
===============================

* CRITICAL error messages from MIP Convert are correctly captured in the
  ``critical_issues.log`` file, and known exceptions from within MIP Convert
  will no longer lead to task failure in CDDS Convert suites (#1533).

Release 1.3.1, January 20, 2020
===============================

* Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)

Release 1.3.0, January 14, 2020
===============================

* No changes.

Release 1.2.3, November 26, 2019
================================

* No changes.

Release 1.2.2, November 13, 2019
================================

* No changes.

Release 1.2.1, October 29, 2019
===============================

* The ``cdds_convert.log`` file is now written to the ``convert/log``
  processing directory rather than the working directory (as seen at v1.2.0)
  (#1341)
* CDDS Convert now ignores streams where there are no |MIP requested variables|
  to be processed rather than raising a ``KeyError`` (#1282)

Release 1.2.0, October 17, 2019
===============================

* The ``--root_config`` command line option for the ``cdds_convert`` script has
  now been removed (all arguments provided by the CDDS configuration files are
  now provided via command line options, see below; #1070)
* The ``--root_proc_dir`` and ``root_data_dir`` command line options for the
  ``cdds_convert`` script have now been added (#1070)

Release 1.1.4, September 2, 2019
================================

* To avoid causing storage issues on SPICE the MIP Convert tasks in the CDDS
  Convert Rose suites now report the local disk usage (if suite variable
  $STAGING_DIR is set). If this limit is specified then tasks that exceed the
  limit will fail (#1158).
* To enable HadGEM3-GC31-MM (N216) processing the requests for local temporary
  storage ($TMPDIR), in the MIP Convert tasks within the Rose suites, have
  been extended (#1158).

Release 1.1.3, July 31, 2019
============================

* No changes.

Release 1.1.2, July 3, 2019
===========================

* Following updates to the MIP Concatenate sizing file to ensure that
  |output netCDF files| containing daily output on model levels are now
  correctly sized (#1002)

Release 1.1.1, June 27, 2019
============================

* No changes.

Release 1.1.0, June 12, 2019
============================

* CDDS Convert now preferentially uses ``cftime``, falling back to using
  ``netcdftime`` if ``cftime`` is not available in the environment (#249)
* A temporary local storage allocation is now requested in SPICE job scripts
  in order to avoid job failures due to lack of disk space (#824) and the
  settings controlling the temporal extent of the output files has been
  updated to include daily IPCC critical variables (#824, #883, #921)
* |MIP requested variables| can now be processed from the ``apm`` |stream|
  (#922)

Release 1.0.5, May 10, 2019
===========================

* No changes.

Release 1.0.4, May 2, 2019
==========================

* Candidate concatenation file is now written to an intermediate directory, so
  that temporary files do not land up in the output directory and then in the
  publication pipeline (#849)
* Fixed a bug where after a timeout, a concatenation task would not produce
  all the expected output (#849)

Release 1.0.3, April 18, 2019
=============================

* Mip_convert and mip_concatenate now write to three separate directories: one
  for mip_convert output, a second for input files to the concatenation tasks
  and a third for the final concatenation tasks which is where qc and transfer
  will look for the output (#840)
* Updated the calculation of the concatenation task cycle time for suites that
  only have 1 scheduled concatenation task due to the short run time (#852)

Release 1.0.2, April 5, 2019
============================

* No changes.

Release 1.0.1, April 2, 2019
============================

* The |stream identifiers| and grid identifiers are now obtained directly from
  the |user configuration files| (#555)
* One Rose suite per |stream identifier| is now submitted rather than one Rose
  suite per request (#710)
* The argument provided to the ``--rose-suite-branch`` parameter can now be a
  path to a checked out version of the Rose suite (for development purposes
  only; #739)
* The Rose suite now removes directories where outputs are written prior to
  producing those outputs (#750)
* The concatenation periods are now aligned with the reference date (#762)
* A single |output netCDF file| is now produced if the concatenation period is
  more than the run bounds (#778)
* The correct files are now included in each concatenation period (#780)
* The cycles to run MIP Convert are now aligned with the reference date (#781)

Release 1.0.0, February 1, 2019
===============================

* First implementation of CDDS.
