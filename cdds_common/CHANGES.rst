.. (C) British Crown Copyright 2021-2022, Met Office.
.. Please see LICENSE.rst for license details.

.. include:: common.txt

Release 2.3.1, June 29, 2022
============================

* Added auto-genereated table of CDDS variable mappings (CDDSO-120)
* Fix inconsistency in case between mip era and plugin name (CDDSO-132)

Release 2.3.0, May 24, 2022
============================

* Development moved to github
* Version string now includes git commit hash (CDDSO-93)

Release 2.2.5, May 4, 2022
============================

* The atmosphere timestep, used in some mappings, is now supplied via the
  ModelParameters class rather than a dictionary. This is only used for request
  JSON file creation (#2571)

Release 2.2.4, April 22, 2022
=============================

* Added UKESM1-1-LL model to CMIP6 and GCModelDev projects (#2545)

Release 2.2.3, April 7, 2022
============================

* No changes

Release 2.2.2, March 18, 2022
=============================

* Addition of GCModelDev plugin with core CMIP6 models (#2519)

Release 2.2.1, February 15, 2022
================================

* UKESM1-ice-LL model information now loaded correctly (#2530)

Release 2.2.0, February 9, 2022
===============================

* New module to take common code across CDDS and will ultimately replace hadsdk (#2460)
* Introduced plugin system for project information (e.g. CMIP6) and model descriptions to
  enable use of CDDS outside of CMIP6 (#2460, #2461, #2462, #2468, #2494, #2502, #2503, #2504,
  #2509, #2510, #2512, #2513, #2514)
* Update to use python 3.8 (#2438)
