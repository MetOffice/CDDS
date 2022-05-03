.. (C) British Crown Copyright 2017-2019, Met Office.
.. Please see LICENSE.rst for license details.

.. _overview:

CDDS Prepare
============

.. include:: common.txt

The CDDS Prepare package enables a user to create the
|requested variables list| and directory structures in preparation for
subsequent CDDS components to be run.

An overview of CDDS Prepare
---------------------------

The following steps are performed to produce the |requested variables list|:

* retrieve the |MIP requested variables| for the |experiment| from the
  specified version of the |data request|
* retrieve the |MIP requested variables| for the |experiment| from the version
  of the |data request| used to setup the |model|
* retrieve the |MIP requested variables| from the model suite.
* determine which |MIP requested variables| can and will be produced based on:

  * whether the |MIP requested variable| is enabled in the |model| suite;
  * whether the |MIP requested variable| has an associated
    |model to MIP mapping|;
  * whether the |MIP requested variable| has changed significantly between the
    version of the |data request| used to setup the |model| and the specified
    version of the |data request|;
  * whether the priority of the |MIP requested variable| (which can differ
    depending on the |MIP|) is equal to or less than the maximum priority,

* write the |requested variables list|.
