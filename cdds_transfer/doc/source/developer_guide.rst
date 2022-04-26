.. (C) British Crown Copyright 2018, Met Office.
.. Please see LICENSE.rst for license details.

.. _dev_guide:

***************
Developer Guide
***************

.. include:: common.txt
.. contents::
   :depth: 2

Overview
========

This document is intended to describe to the developers how the tools within
CDDS Transfer work. This is not intended for users, but to aid developers in
re-familiarising themselves with the code.

Command line tool operation
===========================

Archiving: `send_to_mass`
-------------------------

The process of archiving files using `send_to_mass` involves the following
steps:

1. Obtain command line arguments
2. Set up the logger
3. Read the request JSON file and constructing the Request
   (:class:`hadsdk.request.Request`) object
4. Read the CDDSConfigGeneral (:class:`hadsdk.config.CDDSConfigGeneral`) using
   information in the Request
5. Construct the Config object (:class:`cdds_transfer.config.Config`) required
   by the rest of cdds_transfer from the CDDSConfigGeneral and Request objects.
6. Construct the "fixed facet" object
   (:class:`cdds_transfer.drs.DataRefSyntax`) that describes the various facets
   that we wish to constrain data by, e.g. the `piControl` experiment with
   variant_label `r1i1p1f1`
7. Construct the DataTransfer service
   (:class:`cdds_transfer.dds.DataTransfer`). This object contains most of the
   functional code to find files on disk which match the fixed facets, send the
   data to MASS, perform any state changes (move files in MASS) and send the
   corresponding rabbitMQ messages.
8. Identify the files to be archived (:func:`cdds_transfer.common.find_local`)
9. Log the files to be archived (:func:`cdds_transfer.common.log_filesets`).
10. Perform the archiving of all identified files to the embargoed state (
    :func:`cdds_transfer.archive.send_to_mass`,
    :meth:`cdds_transfer.dds.DataTransfer.send_to_mass`)


State changes and sending RabbitMQ messages: `move_in_mass`
-----------------------------------------------------------

The changing of states in `move_in_mass` follows a similar structure to
`send_to_mass`. Steps 1 to 6 differ only in the level to which the `simulate`
argument is dealt with. `move_in_mass` is tightly bound to MASS and it is
difficult to separate and Mock appropriately (ticket needed). As such
`move_in_mass` is "allowed" to perform moose listing commands when simulating.

7. Load the RabbitMQ credentials from `$HOME/.cdds_credentials`
   (:func:`cdds_transfer.common.load_rabbit_mq_credentials`) and incorporate
   these into the Config object. This allows appropriate security on the
   credentials details which are only needed by the CDDS team in order to
   inform CEDA that data is ready for ingestion or problems have been found. If
   the credentials cannot be found or `move_in_mass` is being run from a server
   that is not on the list of `SYSTEMS_ALLOWED_TO_SEND_MESSAGES`, and the
   `--simulate` argument is not supplied, a RuntimeError is raised.
8. Construct the DataTransfer service
   (:class:`cdds_transfer.dds.DataTransfer`).
9. Find files in mass which match the facets
   (:func:`cdds_transfer.common.find_mass`) and the specified original status.
10. Log the files to be moved (:func:`cdds_transfer.common.log_filesets`).
11. If not simulating perform the moves of data in mass and send messages (
    :func:`cdds_transfer.state_change.move_in_mass`,
    :meth:`cdds_transfer.dds.DataTransfer.change_mass_state`).


Admin messages: `send_admin_msg`
--------------------------------

Not functional, but may be needed to warn CEDA of changes to CDDS
(clarification required).

