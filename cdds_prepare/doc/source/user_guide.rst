.. (C) British Crown Copyright 2017-2019, Met Office.
.. Please see LICENSE.rst for license details.

.. _user_guide:

**********
User Guide
**********

.. include:: common.txt

Quick Start
===========

#. Create the CDDS directory structure::

    % create_cdds_directory_structure -h
    % JSON='{"config_version": "0.5.0", "experiment_id": "ssp119",
             "mip": "ScenarioMIP", "mip_era": "CMIP6",
             "model_id": "UKESM1-0-LL", "package": "phase1",
             "root_data_dir": "my_data_dir", "suite_id": "u-ar766",
             "variant_label": "r1i1p1f1"}'
    % echo $JSON > request.json
    % create_cdds_directory_structure request.json

#. Produce the |requested variables list|::

    % prepare_generate_variable_list -h
    % prepare_generate_variable_list request.json 01.00.20 01.00.13 77678

#. Check the |requested variables list| is as expected (it is named
   ``<mip_era>_<mip>_<experiment>_<model>.json``, e.g.
   ``CMIP6_CMIP_amip_HadGEM3-GC31-LL.json``). For help or to report
   an issue, please see :ref:`support`.

Recommended Reading
===================

1. The :ref:`overview of CDDS Prepare <overview>`

.. _request_json_file:

The request JSON file
=====================

For ``create_cdds_directory structure``, the request JSON file must contain:

    * ``config_version``
    * ``experiment_id``
    * ``mip``
    * ``mip_era``
    * ``model_id``
    * ``package``
    * ``root_data_dir``
    * ``variant_label``

For ``prepare_generate_variable_list``, the request JSON file must contain:

    * ``config_version``
    * ``experiment_id``
    * ``mip``
    * ``mip_era``
    * ``model_id``
    * ``root_data_dir``
    * ``suite_id``

See :class:`hadsdk.request.Request` for more information.

The CDDS configuration files
============================

CDDS Prepare depends on two configuration files arranged in the following
structure::

    <programme>/
        cdds.cfg
        v<config_version>/
            general/
                <programme>.cfg

The root path to the directory containing these CDDS configuration files can be
specified by the ``--root_config`` argument to
``create_cdds_directory_structure`` and ``prepare_generate_variable_list``.

The CDDS directory structure
============================

The CDDS directory structure is as follows:

* data directory = /<dataroot>/<datamap>/
* proc directory = /<procroot>/<procmap>/

where ``<dataroot>`` is provided by ``root_data_dir`` in the request JSON file,
and ``<datamap>``, ``<procroot>`` and ``<procmap>`` are provided by the general
configuration file in the form::

    [locations]
    procroot = /project/cdds/proc

    [facetmaps]
    datamap = programme|project|model|experiment|realisation|package
    procmap = programme|project|experiment|request|package

|Experiments| in the |data request|
===================================

To determine the correct, case-sensitive name for an |experiment| the following
sources can be used:

* The ES-Doc search interface at https://search.es-doc.org/
* The list of experiments in the |data request| at
  http://clipc-services.ceda.ac.uk/dreq/index/experiment.html

The former is easier to use, but the latter is the definitive source for the
**latest version of the data request only**.

Note that new versions of the |data request| can be released with little or no
notice, and as such the online documentation linked to above should be referred
to carefully, i.e. always note the version of the |data request| (available by
clicking the ``Home`` link on the page).

Priorities in the |data request|
================================

The |data request| allows the individual |MIPs| to request
|MIP requested variables| from |experiments| with different priorities (1=high,
3=low). For example, the |MIP requested variable| ``tsl`` in |MIP table|
``Lmon`` has a default priority of 2, but MIPs ``PMIP`` and ``VIACSAB`` have
this |MIP requested variable| from the ``historical`` experiment at a priority
of 1. The priority determined by the ``prepare_generate_variable_list`` script
depends on which |MIPs| are being constributed to. For example, if PMIP and
VIACSAB are contributed to, the |MIP requested variable| ``tsl`` in |MIP table|
``Lmon`` would have a priority of 1.

.. _requested_variables_list:

Requested Variables List
========================

The |requested variables list| contains the following information:

`MAX_PRIORITY`
    The maximum priority to consider when determining whether a
    |MIP requested variable| should be marked ``active``.
`MIPS_RESPONDED_TO`
    The list of |MIPs| for which requests for data were responded to.
`checksum`
    A checksum that is used to validate the |requested variables list|.
`data_request_version`
    The version of the |data request| used to generate the list of
    |MIP requested variables|.
`experiment_id`
    The |experiment identifier|.
`history`
    A list of dated changes that have been made to the
    |requested variables list|.
`mip`
    The |MIP| that owns the |experiment|.
`model_id`
    The |model identifier|.
`suite_branch`
    The branch of the model suite referred to by ``suite_id``.
`suite_id`
    The |suite identifier|.
`revision`
    The revision of the model suite referred to by ``suite_id``.
`production_info`
    A description of the script used to create the |requested variables list|.
`metadata`
    Information describing the versions of the |data request| used and other
    details of the experiment.
`status`
    Set to ``ok`` if there were no errors when attempting to interpret the
    |data request|.
`requested_variables`
    A list of dictionaries describing the |MIP requested variables| for the
    |experiment| from the specified version of the |data request|.

Each element of the ``requested_variables`` list within the
|requested variables list| is a dictionary with the following elements:
     
`active`
    Whether the choice has been made to produce the |MIP requested variable|
    (either ``true`` or ``false``).
`cell_methods`
    The cell methods associated with this |MIP requested variable|.
`comments`
    A list of comments describing why a |MIP requested variable| is not
    ``active``.
`dimensions`
    A list of the dimensions associated with this |MIP requested variable|.
`ensemble_size`
    The ensemble size requested for this |MIP requested variable|.
`frequency`
    The frequency of the |MIP requested variable|.
`in_model`
    Whether the |MIP requested variable| is enabled in the |model| suite.
`in_mapping`
    Whether the |MIP requested variable| has an associated
    |model to MIP mapping|.
`label`
    The |MIP requested variable name|.
`miptable`
    The |MIP table|.
`priority`
    The priority of the |MIP requested variable|.

Modifying |requested variables lists|
=====================================

The |requested variables lists| generated by the
``prepare_generate_variable_list`` script will only contain the
|MIP requested variables| listed in the |data request|. It is possible that
errors in the |data request| will result in inaccuracies in the
|requested variables lists|, and as such the user may need to manually alter
them.

There are two ways to make modifications to a |requested variables list|.
The first is to use the ``prepare_alter_variable_list`` script to alter which
|MIP requested variables| are active. The second is to use the
``prepare_select_variables`` script to specify a subset of
|MIP requested variables| for testing (all other |MIP requested variables|
are deactivated).

The ``prepare_alter_variable_list`` script can be controlled in one of two
ways; via  command line arguments or via a text file describing any number of
command line arguments (this functionality is provided by the
``fromfile_prefix_chars`` argument for :class:`argparse.ArgumentParser`.) The
latter method is the easier method when working with more than a few
|MIP requested variables|. Command line arguments can be found using the
`--help` option, but the following examples should illustrate its use.

Activate some low priority sea-ice |MIP requested variables|::

    prepare_alter_variable_list CMIP6_ScenarioMIP_ssp245_HadGEM3-GC31-LL.json
    activate SImon/siitdthick SImon/siitdsnthick "activate sea ice variables"

Deactivate some tree |MIP requested variables|::

    prepare_alter_variable_list CMIP6_ScenarioMIP_ssp245_HadGEM3-GC31-LL.json
    deactivate Lmon/treeFrac Emon/treeFracBdlDcd Emon/treeFracBdlEvg
    Emon/treeFracNdlDcd "trees aren't wanted any more"

Insert a missing |MIP requested variable|::

    prepare_alter_variable_list CMIP6_ScenarioMIP_ssp245_HadGEM3-GC31-LL.json
    insert 6hrPlev/tas "add missing 6 hourly tas for project X"

To repeat the command above using a text file, create a file called, e.g.
``args.txt`` containing::

    CMIP6_ScenarioMIP_ssp245_HadGEM3-GC31-LL.json
    activate
    SImon/siitdthick
    SImon/siitdsnthick
    activate sea ice variables

then run::

    prepare_alter_variable_list @args.txt

The ``prepare_select_variables`` script operates in the opposite way to the
``prepare_alter_variable_list``, in that it operates on all
|MIP requested variables| except those specified as arguments by the user. The
user specifies the |requested variables list| file as the first argument,
and then a list of the |MIP requested variables| to be tested by the
other CDDS components::

    prepare_select_variables CMIP6_ScenarioMIP_ssp245_HadGEM3-GC31-LL.json
    Amon/tas Amon/uas Amon/pr Amon/vas Omon/Pr

In this example, all the |MIP requested variables| other than those listed will
be deactivated in the |requested variables list| file and subsequently not
processed. This is intended for development and testing purposes.

**Important: In all of the above cases the original file is overwritten.**
