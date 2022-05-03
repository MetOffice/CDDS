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

CDDS QC provides means to test compliance with the CF Metadata Conventions,
along with additional data quality checks specific to the CMIP6 project, such
as looking for gaps in data, mandatory global attributes, properly formatted
variable meta-data, and consistency with Controlled Vocabularies.

To run and generate QC report use the ``bin/qc_run_and_report`` script.

Parameters
----------

``request``
    Path to the json file containing data request information.
``root_config``
    Root of the CDDS config directory (defaults to ``/project/cdds/config``).
``mip_table``
    If provided, the QC will be run only for this particular mip table.
``start``, ``end``
    If provided, the QC will be run for provided time slice. Accepts any
    reasonable, well-ordered data format, e.g. ``YYYY``, ``YYYYMM``,
    ``YYYYMMDD``.

For example::

    run_and_report --request ~cdds/ete5/abrupt-4xCO2/request.json \
     --root_config ~cdds/ete5/abrupt-4xCO2/transfer_for_215/

The report is in a form of JSON file, which by default is saved under the
``qualitycheck`` section of request's ``proc`` directory.

The file contains two main sections: ``aggregated_summary``, which lists all
errors by type and MIP table, along with affected variables, e.g.:

.. code-block:: json

    {
        "aggregated_summary": [
            {
                "checker": "cmip6",
                "error_message": "Global attributes check: Cannot retrieve variable attribute cell_measures",
                "affected_vars": "wo|vmo|umo|tauuo|tauvo",
                "affected_files": 15,
                "mip_table": "Omon"
            },
            {
                "checker": "cf17",
                "error_message": "§3.3 Variable mrsll has valid standard_name attribute: standard_name liquid_moisture_content_of_soil_layer is not defined in Standard Name Table v58",
                "affected_vars": "mrsll",
                "affected_files": 3,
                "mip_table": "Emon"
            }
        ]
    }

There is also a separate ``details`` section listing all individual files and
errors.

.. code-block:: json

    {
        "details": [
            {
                "mip_table_filter": "all",
                "db_id": 1,
                "results": [
                    {
                        "variable": "agessc",
                        "experiment": "abrupt-4xCO2 ",
                        "errors": "Global attributes check: Mandatory attribute external_variables: Value: areacello volcello, Expected: areacella, areacello",
                        "mip_table": "Omon",
                        "filename": "agessc_Omon_HadGEM3-GC31-LL_abrupt-4xCO2_r2i1p1f1_gn_185001-186912.nc"
                    }
                ]
            }
        ]
    }

The header contain some additional information related to the way the QC tool
has been run, but in the production environment it can be ignored (as the tool
will be run in a single-threaded, non-filtered mode).
