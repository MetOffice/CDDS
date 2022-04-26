.. (C) British Crown Copyright 2017-2019, Met Office.
.. Please see LICENSE.rst for license details.

.. _overview:

CDDS Convert
============

.. include:: common.txt

The CDDS Convert package is a tool to wrap `mip_convert`, managing the
submission of multiple processes to batch clusters through a Rose suite and
reporting progress.

An overview of CDDS Convert
---------------------------

The core of CDDS Convert is the :class:`cdds_convert.process.ConvertProcess` 
class which inherits from :class:`hadsdk.process.CDDSProcess`. When initialised
this class obtains information on a particular |request|, either from CREM
or a supplied JSON structure, and proceeds through the following stages;

 * instatiation/bootstrap: obtains information and sets up log files.
 * checkout conversion suite: checks out a Rose suite to perform the necessary
   conversions.
 * updates suite parameters: sets various parameters within the
   `rose-suite.conf` file appropriately.
 * submission: submits the Rose suite to a batch cluster.
 * shutdown: reports status to log and exits.
 
Additional tools allow the user to identify whether a suite is running and how
many of its tasks have completed successfully.

Notes on vocabulary
-------------------

The nomenclature around CMIP data can be complex and to avoid confusion it
would be good if consistent vocabulary could be used. To this end please use
vocabulary from the :doc:`glossary`, such as |MIP requested variable|, where
possible.
