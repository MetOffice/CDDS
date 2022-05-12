.. (C) British Crown Copyright 2018-2022, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

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

* QC checks now refer to provided controlled vocabulary for non-CMIP6 projects (#2542)

Release 2.2.1, February 15, 2022
================================

* No changes.

Release 2.2.0, February 9, 2022
===============================

* Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* Update to use python 3.8 (#2438)
* CDDS QC now uses the community version of IOOS/compliance-checker rather than a fork (#2381)
* Allow for the use of CDDS beyond CMIP6 (#2449, #2469, #2470)

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

* No changes.

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

* The ``cell_measures`` validation is now properly processing variables with ``--MODEL`` flag
  (#2193)

Release 1.6.1, November 26, 2020
================================

* The ``cell_measures`` validation is now properly processing global averages (#2171)

Release 1.6.0, November 05, 2020
================================

* Consistency checks for ``netCDF`` variable attributes are now correctly applied (#2001)
* Replaced the ``CMIP6`` ``Controlled Vocabulary`` tables with the ones bundled
  with ``CMOR`` (#1808)

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

* Fixed a bug that prevented from validation of some global attributes of
  simulations without a parent experiment (#2000)

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

* CDDS QC now handles variables where the ``cell_measures`` variable attribute
  is optional (#1801)

Release 1.4.1, April 28, 2020
=============================

* No changes.

Release 1.4.0, April 23, 2020
=============================

* No changes.

Release 1.3.4, March 27, 2020
=============================

* No changes.

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

* No changes.

Release 1.2.3, November 26, 2019
================================

* No changes.

Release 1.2.2, November 13, 2019
================================

* No changes.

Release 1.2.1, October 29, 2019
===============================

* No changes.

Release 1.2.0, October 17, 2019
===============================

* CDDS QC now confirms that the ``parent_experiment_id`` attribute in
  the |output netCDF files| is consistent with the ``Request`` and
  |Controlled Vocabulary|, allowing for the choice of ``parent_experiment_id``
  where there are options within the |Controlled vocabulary| (#1083)

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
* Fixed a bug in CF Standard Names parser that prevented validation of
  `Emon/ta` (#993).

Release 1.1.0, June 12, 2019
============================

* The CMIP6 Compliance Checker Plugin now preferentially uses ``cftime``,
  falling back to using ``netcdftime`` if ``cftime`` is not available in the
  environment (#249)

Release 1.0.5, May 10, 2019
===========================

* No changes.

Release 1.0.4, April 30, 2019
=============================

* The validation of the ``activity_id`` global attribute in
  |output netCDF files|, as written by |CMOR|, now allows for multiple |MIPs|
  to be specified in the CMIP6 |Controlled Vocabulary| for a particular
  |experiment|. For example, data produced for |experiment| ``ssp370`` should
  have an ``activity_id`` of ``ScenarioMIP AerChemMIP`` (#865)

Release 1.0.3, April 5, 2019
============================

* No changes

Release 1.0.2, April 5, 2019
============================

* No changes.

Release 1.0.1, April 2, 2019
============================

* No changes.

Release 1.0.0, February 1, 2019
===============================

* First implementation of CDDS.
