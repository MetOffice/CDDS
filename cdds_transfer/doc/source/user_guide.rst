.. (C) British Crown Copyright 2018, Met Office.
.. Please see LICENSE.rst for license details.

.. _user_guide:

**********
User Guide
**********

.. include:: common.txt
.. contents::
   :depth: 2


Quick Start
===========

1. Archive data to MASS identified by a request JSON file::

    $ send_to_mass -h
    $ send_to_mass request.json -l test.log --simulate
    $ send_to_mass request.json -l archive.log

   Note that this should only be run from SPICE, unless using the `simulate`
   option.
2. Submit data for ingestion by CEDA::

    $ move_in_mass -h
    $ move_in_mass request.json -o embargoed -n available -l test.log --simulate
    $ move_in_mass request.json -o embargoed -n available -l submit.log

   Note that `move_in_mass` can only be run on particular systems by CDDS team
   members, unless using the `simulate` option.
3. Withdraw data that has already been published::

    $ move_in_mass request.json -o available -n withdrawn -l test.log --simulate
    $ move_in_mass request.json -o available -n withdrawn -l withdraw.log


Recommended Reading
===================

1. The :ref:`overview of CDDS Transfer <overview>`


Request JSON file
=================

Required keys
-------------

The request JSON file needs to contain at least the following keys

`config_version`
   The config version to use
`mip_era`
   The |MIP era|.
`institution_id`
   The `institution_id` as specified in the |Controlled Vocabulary|, e.g.
   `MOHC`.
`mip`
   The |MIP|.
`model_id`
   The |model identifier|.
`experiment_id`
   The `experiment_id`, e.g. `piControl`,
`package`
   The package is a string that identifies a particular chunk of work on a
   particular simulation, e.g. `ETE5`.
`variant_label`
   The |variant label|

Optional keys
-------------

Additional keys that are listed in the `[transfer_facetmaps]` section of the
general config file may also be used to constrain the archiving and sending of
messages relating to state changes. For example including `table_id` would
allow state changes on a per |MIP table| basis.

Credentials file
================

For sending messages to the Rabbit MQ server a set of details describing the
server and the credentials needed to connect.  This config file must be placed
at `$HOME/.cdds_credentials` and must only be accessible by the current user.
The credentials file must have the following structure::

    [rabbit]
    host = <host name of Rabbit MQ server>
    port = <TCP/IP port to connect to>
    userid = <User name>
    use_plain = true
    vhost = <virtual host name>
    password = <password>

As noted above these credentials will only be needed by the CDDS team
