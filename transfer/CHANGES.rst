.. (C) British Crown Copyright 2019-2022, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

Release 2.3.2, September 01, 2022
=================================

* No changes.

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

* Removed further calls to the moo test command when archiving data (#2559, #2560)

Release 2.2.3, April 7, 2022
============================

* moose listing commands are used rather than `moo test` in order to limit the number
  of commands talking to MASS, thereby limiting our vulnerability to transient or load
  dependent errors, and increases performance (#2553)

Release 2.2.2, March 18, 2022
=============================

* No changes

Release 2.2.1, February 15, 2022
================================

* No changes.

Release 2.2.0, February 9, 2022
===============================

* Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* Update to use python 3.8 (#2438)

Release 2.1.2, November 25, 2021
================================

* No changes.

Release 2.1.1, October 26, 2021
===============================

* Added scripts for listing submission queues and resending stored messages that failed during submission
  (#2427, #2428)

Release 2.1.0, September 6, 2021
================================

* `cdds_store` is now run as part of the conversion suite by `cdds_convert` by default (#1902,
  #2425, #2432)
* `cdds_sim_review` now handles per stream logs, qc reports and approved variables files
  (#1685)

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

* Allow for correct handling of packages where there are multiple mips / activity ids.
  The primary, i.e. first, mip will be used for all directory and dataset ids (#2369)

Release 2.0.3, April 28, 2021
=============================

* CDDS store can now prepend files to an embargoed dataset provided the
  correct data version argument is provided (#2278)

Release 2.0.2, April 22, 2021
=============================

* No changes.

Release 2.0.1, March 25, 2021
=============================

* CDDS store can now recover gracefully when continuing archiving following
  task failure due to issues with MASS (#2205)
* CDDS store can now correctly handle pre-pending files to datasets and there are
  clearer error messages when issues arise (#2222)

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

* The failure of `moo put` commands is now handled more clearly (#2212)

Release 1.6.2, January 11, 2021
===============================

* No changes.

Release 1.6.1, November 26, 2020
================================

* No changes.

Release 1.6.0, November 05, 2020
================================

* No changes.

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

* cdds_store can now archive CF sites datawith frequency subhrPt (#1945)
* cdds_store will now raise CRITICAL log messages, rather than ERROR when
  something goes wrong (#1934)

Release 1.5.0, July 2, 2020
===========================

* No changes.

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

* No changes.

Release 1.3.4, March 27, 2020
=============================

* Errors arising from MOO failures are now properly handled and logged (#1701)

* Transfer now supports processing variables with different output names to
  their variable ID, and has better support for processing a single stream
  using the --stream command line option (#1622)

Release 1.3.3, February 25, 2020
================================

* No changes.

Release 1.3.2, January 27, 2020
===============================

* ``cdds_store`` now handles experiment ids including the ``-`` character
  (#1556)

Release 1.3.1, January 20, 2020
===============================

* Moved to updated scitools environment production_legacy-os43-1;
  python v2.7, iris v2.2 (#1512)
* ``cdds_store_spice`` now passes all arguments through to spice job (#1511)
* ``cdds_store`` behaves correctly when there are no files to archive (#1520)

Release 1.3.0, January 14, 2020
===============================

* Added new archiving tool ``cdds_store`` to replace ``send_to_mass`` and
  ``cdds_transfer_spice`` (#1384)

Release 1.1.0, June 12, 2019
============================

* No changes.

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

* No changes.

Release 1.0.0, February 1, 2019
===============================

* First implementation of CDDS.
