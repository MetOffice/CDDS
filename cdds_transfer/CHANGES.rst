.. (C) British Crown Copyright 2018-2022, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

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

* No changes

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

Release 2.1.2, November 25, 2021
================================

* No changes.

Release 2.1.1, October 26, 2021
===============================

* No changes.

Release 2.1.0, September 6, 2021
================================

* No changes.

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

* All exceptions caught at the top script level are now logged as critical errors (#1968)

Release 1.5.5, October 20, 2020
===============================

* ``move_in_mass`` now correctly includes variables, where the
  |MIP requested variable name| and name used in the output file is different,
  when submitting data for publication (#2049).

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

* ``move_in_mass`` now only lists directories in MASS connected with
  the Request provided, significantly reducing run time (#1649).

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
* Added new archiving tool ``cdds_store`` to replace ``send_to_mass`` and
  ``cdds_transfer_spice`` (#1384)

Release 1.2.3, November 26, 2019
================================

* No changes.

Release 1.2.2, November 13, 2019
================================

* The failure to submit a RabbitMQ message, which triggers the publication
  process, is now accompanied by a critical log message (#1346)

Release 1.2.1, October 29, 2019
===============================

* No changes.

Release 1.2.0, October 17, 2019
===============================

* The ``send_to_mass`` and ``cdds_transfer_spice`` scripts now raise critical
  log messages rather than error log messages, where appropriate (#1045)

Release 1.1.4, September 2, 2019
================================

* No changes.

Release 1.1.3, July 31, 2019
============================

* To ensure messages sent to CEDA when withdrawing data contain the correct
  version date stamp, the version date stamp used in the path in MASS now
  doesn't change during state changes (#919)

Release 1.1.2, July 3, 2019
===========================

* No changes.

Release 1.1.1, June 27, 2019
============================

* No changes.

Release 1.1.0, June 12, 2019
============================

* No changes.

Release 1.0.5, May 10, 2019
===========================

* No changes.

Release 1.0.4, May 2, 2019
==========================

* Added command line option to ``move_in_mass`` script to allow state changes,
  such as ``embargoed`` to ``available`` or ``available`` to ``withdrawn``, to
  be limited to a list of variables (#876)

Release 1.0.3, April 18, 2019
=============================

* The MOOSE ``command-id`` is now reported via ``run_moo_cmd`` to allow CEDA's
  CREPP tools to kill processes left running on the MOOSE controllers that
  should have ended when the command line MOOSE client exited (#855)

Release 1.0.2, April 5, 2019
============================

* No changes.

Release 1.0.1, April 2, 2019
============================

* The new command line script ``cdds_transfer_spice`` can now be used to run
  CDDS Transfer on SPICE (#688)
* The name of the directory used to store |output netCDF files| on MASS can now
  be specified via the ``--mass_location`` parameter (#756)
* The SPICE logs for ``cdds_transfer_spice`` are now written to the correct
  location when using the ``--use_proc_dir`` parameter (#828)

Release 1.0.0, February 1, 2019
===============================

* First implementation of CDDS.
