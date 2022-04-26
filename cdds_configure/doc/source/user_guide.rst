.. (C) British Crown Copyright 2018-2019, Met Office.
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

#. Create a template |user configuration file| for an experiment with no parent
   and including the default arguments::

    % cdds_configure -h
    % JSON='{"branch_method": "no parent", "calendar": "360_day",
             "child_base_date": "1850-01-01-00-00-00",
             "experiment_id": "amip", "mip": "CMIP", "mip_era": "CMIP6",
             "model_id": "UKESM1-0-LL", "model_type": "AGCM",
             "package": "cdds-example-1", "sub_experiment_id": "none",
             "suite_branch": "cdds", "suite_id": "u-abcde",
             "suite_revision": "104874", "variant_label": "r1i1p1f1"}'
    % echo $JSON > request.json
    % cdds_configure request.json --template --use_proc_dir

The request JSON file
=====================

The minimum the request JSON file must contain (which occurs when
``branch_method`` has an argument of ``no parent`` and the ``--template``
option is used) is:

    * ``branch_method``
    * ``calendar``
    * ``child_base_date``
    * ``experiment_id``
    * ``mip``
    * ``mip_era``
    * ``model_id``
    * ``model_type``
    * ``sub_experiment_id``
    * ``suite_branch``
    * ``suite_id``
    * ``suite_revision``
    * ``variant_label``

If using the ``--use_proc_dir`` option, the request JSON file must also
contain:

    * ``package``

If the argument of ``branch_method`` is anything other than ``no parent``, the
request JSON file must also contain:

    * ``branch_date_in_child``
    * ``branch_date_in_parent``
    * ``parent_base_date``
    * ``parent_mip_era``
    * ``parent_model_id``
    * ``parent_time_units``
    * ``parent_variant_label``

The  ``--template`` option will replace the arguments for the following
parameters with Jinja2 templating:

    * ``cmor_log_file``
    * ``model_output_dir``
    * ``output_dir``
    * ``run_bounds``

If the ``--template`` option is not specified, the following parameters must be
included in the request JSON file:

    * ``model_output_dir``
    * ``output_dir``
    * ``run_bounds``

It is not necessary to specify arguments for the following parameters, since
there are defaults available (see :mod:`cdds_configure.arguments`):

    * ``ancil_files``
    * ``create_subdirectories``
    * ``deflate_level``
    * ``hybrid_heights_files``
    * ``institution_id``
    * ``license``
    * ``netcdf_file_action``
    * ``replacement_coordinates_file``
    * ``shuffle``
    * ``sites_file``

If arguments for any of these parameters are specified in the request JSON
file, they will be used preferentially over the defaults.
