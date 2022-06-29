.. (C) British Crown Copyright 2016-2022, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

Release 2.3.1, June 29, 2022
============================

* remove_ocean_haloes script now works after change to load plugin (CDDSO-152)

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

* MASS paths with and without the ensemble_id in them are now handled (#2522)

Release 2.2.2, March 18, 2022
=============================

* No changes.

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

* Extract will now repeat creating stream directories if the first time fails because
  of intermittent filesystem issues (#2429)

Release 2.1.1, October 26, 2021
===============================

* Added the ``path_reformatter`` command line tool from the cdds_utils directory (#2415)

Release 2.1.0, September 6, 2021
================================

* `cdds_extract` is now run as part of the conversion suite by `cdds_convert` by default
  (#1902, #2425)

Release 2.0.8, August 3, 2021
=============================

* No changes.

Release 2.0.7, July 15, 2021
============================

* The ``remove_ocean_haloes`` command line tool is now available to remove halo rows and
  columns from ocean data files (#1161)

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

* No changes.

Release 2.0.1, March 25, 2021
=============================

* When running for a particular stream the stream name is now included in the
  log file name (#2014)

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

* Fixed a bug in the validation report, where the expected number of files would be printed
  instead of the actual file count (#2174)

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

* Information on the validation of the is now written to <stream>_validation.txt
  as well as to the log files (#1811)

Release 1.5.0, July 2, 2020
===========================

* CDDS Extract now correctly reports failure through error codes and e-mails
  (#1807)
* CDDS Extract can now correctly retrieve daily MEDUSA data (#1803)

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

* Extract can now extract data from sub-daily PP streams (#359)
* Extract processes for individual streams can now be run in separate tasks
  (#1619)

Release 1.3.4, March 27, 2020
=============================

* No changes.

Release 1.3.3, February 25, 2020
================================

* Extract will no longer log CRITICAL errors when processing data
  streams containing no retrievable variables (#1583, #1354).

Release 1.3.2, January 27, 2020
===============================

* Clarified CRITICAL messages when PP files are found to be incomplete
  (#1528)
* Extract does not now raise an error when attempting to interpret the
  request file for ``HadGEM3-GC31-MM`` packages (#1563)

Release 1.3.1, January 20, 2020
===============================

* Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)

Release 1.3.0, January 14, 2020
===============================

* CDDS Extract no longer connects to CREM to retrieve request information
  (#1079, #1080).
* ``--root_proc_dir`` and ``--root_data_dir`` arguments are now correctly
  interpreted by the ``cdds_extract_spice`` command (#1478).
* Error messages related to unreadable pp files are now being correctly
  logged (#1154).

Release 1.2.3, November 26, 2019
================================

* No changes.

Release 1.2.2, November 13, 2019
================================

* CDDS Extract will now log WARNING rather than CRITICAL messages when there
  are no variables to be extracted for a stream (#1354)
* All moose commands are now non-resumable, in order to avoid cases where MASS
  outages lead to conflicts with CDDS Extract processes (#1374)

Release 1.2.1, October 29, 2019
===============================

* A bug in the |netCDF| validation process, introduced in v1.2.0, that
  resulted in all NEMO model output files being incorrectly identified as
  unreadable, and then deleted, has been fixed (#1333)

Release 1.2.0, October 17, 2019
===============================

* CDDS Extract now handles ``TSSC_SPANS_TOO_MANY_RESOURCES`` errors raised by
  ``moo`` commands that attempt to access files on too many tapes (#814)

Release 1.1.4, September 2, 2019
================================

* When validating |netCDF| model output files, Extract now identifies faulty
  files with no time records (#992).

Release 1.1.3, July 31, 2019
============================

* To avoid issues related to extracting a large number of netCDF
  |model output files| from MASS, the extraction is now performed in multiple
  chunks (#991)

Release 1.1.2, July 3, 2019
===========================

* No changes.

Release 1.1.1, June 27, 2019
============================

* Faulty |model output files| are now removed when issues are identified (#918).

Release 1.1.0, June 12, 2019
============================

* Daily ocean data can now be extracted from MASS (#882)
* Extract logs now contain the CRITICAL keyword for critical issues (#903)
* ``Exceeded step memory limit`` errors in ``cdds_extract_spice`` have been
  resolved (#915)
* The production of MEDUSA ocean biogeochemistry |MIP requested variables| are
  now supported (#582)

Release 1.0.5, May 10, 2019
===========================

* No changes.

Release 1.0.4, April 30, 2019
=============================

* Some unit test utility functions were moved from extract to hadsdk (#865).

Release 1.0.3, April 5, 2019
============================

* No changes

Release 1.0.2, April 5, 2019
============================

* No changes.

Release 1.0.1, April 2, 2019
============================

* A workaround was implemented to deal with the fact that the ``moo ls``
  command sometimes returns a truncated list of filenames (#771)

Release 1.0.0, February 1, 2019
===============================

* First implementation of CDDS.
