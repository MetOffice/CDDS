.. Copyright (C) British Crown (Met Office) & Contributors.
.. Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
.. See the LICENSE file in the top level of this repository for full details.

.. _overview:

MIP Convert
===========

.. include:: common.txt

The MIP Convert package enables a user to produce the |output netCDF files| for
a |MIP| using |model output files|.

An overview of MIP Convert
--------------------------

* The user makes requests for one or more |MIP requested variables| by
  providing specific information (including the appropriate
  |MIP requested variable names|) in the |user configuration file|.
* The information required to produce the |MIP requested variables| is gathered
  from the |user configuration file|, the
  |model to MIP mapping configuration files| and the appropriate |MIP table|,
  in that order.
* The following steps are then performed for each
  |MIP requested variable name| in the |user configuration file| to produce the
  |output netCDF files|:

  * load the relevant data from the |model output files| into one or more
    |input variables| depending on whether there is a one-to-one / simple
    arithmetic relationship between the |MIP output variable| and the
    |input variables| or if the |MIP output variable| is based on an arithmetic
    combination of two or more |input variables|, respectively, using |Iris|
    and the information provided in the |user configuration file| and the
    |model to MIP mapping configuration files|.
  * process the |input variable| / |input variables| to produce the
    |MIP output variable| using the information provided in the
    |model to MIP mapping configuration files|.
  * save the |MIP output variable| to an |output netCDF file| using |CMOR| and
    the information provided in the |user configuration file| and the
    appropriate |MIP table|.
