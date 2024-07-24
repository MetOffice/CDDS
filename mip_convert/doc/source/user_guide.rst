.. (C) British Crown Copyright 2015-2019, Met Office.
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

1. Download the template |user configuration file| (`mip_convert.cfg`_).

2. Make the appropriate edits to the template |user configuration file| using
   the information provided in the 
   :ref:`User configuration file <user_configuration_file>` section and the
   specified sections in the `CMOR Documentation`_.

3. Produce the |output netCDF files|::

   % mip_convert -h
   % mip_convert mip_convert.cfg

4. Check the exit code::

   % echo $?

   If the exit code is equal to 1, an exception was raised and no
   |MIP requested variables| were produced. If the exit code is equal to 2, one
   or more |MIP requested variables| were produced; the ``CRITICAL`` messages
   in the log will provide further information about the
   |MIP requested variables| that were not produced. 

5. Check the |output netCDF files| are as expected. For help or to report an
   issue, please see :ref:`support`.

Selected Arguments
==================

1. ``config_file`` - The name of the user configuration file. For more information,
   please see the MIP Convert user guide:
   https://code.metoffice.gov.uk/doc/cdds/mip_convert/user_guide.html

2. ``-s`` or ``--stream_identifiers`` - The stream identifiers to process. If all streams
   should be processed, do not specify this option.

3. ``--relaxed-cmor`` - If specified, CMIP6 style validation is not performed by CMOR. If the
   validation is run then the following fields are not checked; ``model_id`` (``source_id``),
   ``experiment_id``, ``further_info_url``, ``grid_label``, ``parent_experiment_id``,
   ``sub_experiment_id``.

4. ``--mip_era`` - The MIP era (e.g. CMIP6).

5. ``--external_plugin`` - Module path to external CDDS plugin (e.g. ``arise.plugin``)

6. ``--external_plugin_location`` - Path to the external plugin implementation
   (e.g. ``/project/cdds/arise``)

Example
-------

a. Run for CMIP6 projects:
   ``mip_convert.cfg -s ap4``

b. Run for Non-CMIP6 projects for example for ARISE projects:
   ``mip_convert.cfg -s ap4 --mip_era ARISE --relaxed_cmor --external_plugin arise.plugin --external_plugin_location /projects/cdds/arise``

Recommended Reading
===================

1. The :ref:`overview of MIP Convert <overview>`
2. The `Design Considerations and Overview`_ section in the
   `CMOR Documentation`_

Configuration Files
===================

MIP Convert uses a number of configuration files:

1. :ref:`User configuration file <user_configuration_file>`
2. |Model to MIP mapping configuration files| 
3. |MIP tables|

.. _user_configuration_file:

User Configuration File
-----------------------

The |user configuration file| provides the information required by MIP Convert
to produce the |output netCDF files| and contains the following sections:

1. :ref:`cmor_setup <cmor_setup_section>` [required]
2. :ref:`cmor_dataset <cmor_dataset_section>` [required]
3. :ref:`request <request_section>` [required]
4. :ref:`stream_\<stream_id\> <stream_stream_id>` [required]
5. :ref:`global_attributes <global_attributes>` [optional]

.. _cmor_setup_section:

The ``cmor_setup`` Section
^^^^^^^^^^^^^^^^^^^^^^^^^^

The required :ref:`cmor_setup <cmor_setup_section>` section contains the
following options, which are used by ``cmor_setup``:

+---------------------------+-------------+-------------+-------+
|          Option           | Required by |   Used by   | Notes |
+===========================+=============+=============+=======+
| ``mip_table_dir``         | MIP Convert | MIP Convert | [1]   |
|                           |             | and |CMOR|  |       |
+---------------------------+-------------+-------------+-------+
| ``netcdf_file_action``    |             | |CMOR|      |       |
|                           |             |             |       |
+---------------------------+-------------+-------------+-------+
| ``set_verbosity``         |             | |CMOR|      |       |
|                           |             |             |       |
+---------------------------+-------------+-------------+-------+
| ``exit_control``          |             | |CMOR|      |       |
|                           |             |             |       |
+---------------------------+-------------+-------------+-------+
| ``cmor_log_file``         |             | |CMOR|      | [2]   |
|                           |             |             |       |
+---------------------------+-------------+-------------+-------+
| ``create_subdirectories`` |             | |CMOR|      | [3]   |
|                           |             |             |       |
+---------------------------+-------------+-------------+-------+

[1] See ``inpath`` in the documentation for `cmor_setup`_.

[2] See ``logfile`` in the documentation for `cmor_setup`_.

[3] |CREM| users should set ``create_subdirectories`` to ``0`` to instruct
|CMOR| to write the |output netCDF files| directly to ``output_dir``, which
will already have the correct path subdirectory structure.

For a description of each option, please see `cmor_setup`_.

.. _cmor_dataset_section:

The ``cmor_dataset`` Section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The required :ref:`cmor_dataset <cmor_dataset_section>` section contains the
following options, which are used by `cmor_dataset_json`_:

+---------------------------------+--------------+-------------+-------+
|              Option             | Required by  |   Used by   | Notes |
+=================================+==============+=============+=======+
| ``branch_method``               | MIP Convert  | MIP Convert | [1]   |
|                                 | and |CMOR|   | and |CMOR|  |       |
+---------------------------------+--------------+-------------+-------+
| ``calendar``                    | MIP Convert  | MIP Convert | [2]   |
|                                 | and |CMOR|   | and |CMOR|  |       |
+---------------------------------+--------------+-------------+-------+
| ``comment``                     |              | |CMOR|      | [1]   |
|                                 |              |             | [3]   |
+---------------------------------+--------------+-------------+-------+
| ``contact``                     |              | |CMOR|      | [1]   |
|                                 |              |             |       |
+---------------------------------+--------------+-------------+-------+
| ``experiment_id``               | MIP Convert  | MIP Convert | [1]   |
|                                 | and |CMOR|   | and |CMOR|  |       |
+---------------------------------+--------------+-------------+-------+
| ``grid``                        | |CMOR|       | |CMOR|      | [1]   |
+---------------------------------+--------------+-------------+-------+
| ``grid_label``                  | |CMOR|       | |CMOR|      | [1]   |
+---------------------------------+--------------+-------------+-------+
| ``institution_id``              | MIP Convert  | MIP Convert | [1]   |
|                                 | and |CMOR|   | and |CMOR|  |       |
+---------------------------------+--------------+-------------+-------+
| ``license``                     | |CMOR|       | |CMOR|      | [1]   |
+---------------------------------+--------------+-------------+-------+
| ``mip``                         | |CMOR|       | |CMOR|      | [1]   |
|                                 |              |             | [4]   |
+---------------------------------+--------------+-------------+-------+
| ``mip_era``                     | MIP Convert  | MIP Convert | [1]   |
|                                 | and |CMOR|   | and |CMOR|  |       |
+---------------------------------+--------------+-------------+-------+
| ``model_id``                    | MIP Convert  | MIP Convert | [1]   |
|                                 | and |CMOR|   | and |CMOR|  | [5]   |
+---------------------------------+--------------+-------------+-------+
| ``model_type``                  | |CMOR|       | |CMOR|      | [1]   |
|                                 |              |             | [6]   |
+---------------------------------+--------------+-------------+-------+
| ``nominal_resolution``          | |CMOR|       | |CMOR|      | [1]   |
+---------------------------------+--------------+-------------+-------+
| ``output_dir``                  | MIP Convert  | MIP Convert | [7]   |
|                                 | and |CMOR|   | and |CMOR|  |       |
+---------------------------------+--------------+-------------+-------+
| ``output_file_template``        |              | |CMOR|      |       |
|                                 |              |             |       |
+---------------------------------+--------------+-------------+-------+
| ``output_path_template``        |              | |CMOR|      |       |
|                                 |              |             |       |
+---------------------------------+--------------+-------------+-------+
| ``references``                  |              | |CMOR|      | [1]   |
|                                 |              |             |       |
+---------------------------------+--------------+-------------+-------+
| ``sub_experiment_id``           | MIP Convert  | MIP Convert | [1]   |
|                                 | and |CMOR|   | |CMOR|      |       |
+---------------------------------+--------------+-------------+-------+
| ``variant_info``                |              | |CMOR|      | [1]   |
|                                 |              |             |       |
+---------------------------------+--------------+-------------+-------+
| ``variant_label``               | MIP Convert  | MIP Convert | [1]   |
|                                 | and |CMOR|   | and |CMOR|  |       |
+---------------------------------+--------------+-------------+-------+

[1] For a description of each option, please see the
`CMIP6 Global Attributes document`_.

[2] See calendars for allowed values.

[3] It is recommended to use the ``comment`` to record any perturbed physics
details.

[4] See |MIP|.

[5] See |model identifier|.

[6] See |model type|.

[7] See ``outpath`` in the documentation for `cmor_dataset_json`_.

MIP Convert determines:

* the ``experiment``, ``institution``, ``source``, ``sub_experiment`` from the
  CV file using the ``experiment_id``, ``institution_id``, ``source_id`` and
  ``sub_experiment_id``, respectively
* the ``forcing_index``, ``initialization_index``, ``physics_index`` and
  ``realization_index`` from the ``variant_label``
* the ``further_info_url`` and ``tracking_prefix`` based on the information
  from the CV file
* the ``history``

Whenever a parent exists, the following options must be specified:

+---------------------------------+-----------------+-----------+
|              Option             |     Used by     |   Notes   |
+=================================+=================+===========+
| ``branch_date_in_child``        | MIP Convert     | [1][2][3] |
+---------------------------------+-----------------+-----------+
| ``branch_date_in_parent``       | MIP Convert     | [1][2][3] |
+---------------------------------+-----------------+-----------+
| ``parent_base_date``            | MIP Convert     | [1][2]    |
+---------------------------------+-----------------+-----------+
| ``parent_experiment_id``        | |CMOR|          | [3]       |
+---------------------------------+-----------------+-----------+
| ``parent_mip_era``              | |CMOR|          | [3]       |
+---------------------------------+-----------------+-----------+
| ``parent_model_id``             | |CMOR|          | [3][4]    |
+---------------------------------+-----------------+-----------+
| ``parent_time_units``           | |CMOR|          | [3]       |
+---------------------------------+-----------------+-----------+
| ``parent_variant_label``        | |CMOR|          | [3]       |
+---------------------------------+-----------------+-----------+

[1] CMOR requires ``branch_time_in_child`` and ``branch_time_in_parent``, which
is determined from the options ``base_date`` (see the
:ref:`request <request_section>` section) / ``parent_base_date`` (the
base date of the ``child_experiment_id`` / ``parent_experiment_id``) and
``branch_date_in_child`` / ``branch_date_in_parent`` (the date in the
``child_experiment_id`` / ``parent_experiment_id`` from which the experiment
branches) from the :ref:`cmor_dataset <cmor_dataset_section>` section in the
|user configuration file| by taking the difference (in days) between the
``branch_date_in_child`` / ``branch_date_in_parent`` and the
``base_date`` / ``parent_base_date``. If ``branch_date_in_child`` or
``branch_date_in_parent`` is ``N/A`` then ``branch_time_in_parent`` is set to
0. 

[2] Dates should be provided in the form ``YYYY-MM-DD-hh-mm-ss``.

[3] For a description of each option, please see the
`CMIP6 Global Attributes document`_.

[4] See ``parent_source_id`` in the `CMIP6 Global Attributes document`_.

.. _request_section:

The ``request`` Section
^^^^^^^^^^^^^^^^^^^^^^^

The required :ref:`request <request_section>` section contains the following
options, which are used by MIP Convert:

+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
|                Option                | Required by | Used only by |                    Description                   | Notes |
+======================================+=============+==============+==================================================+=======+
| ``ancil_files``                      |             | MIP Convert  | A space separated list of the full paths to any  |       |
|                                      |             |              | required ancillary files.                        |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``atmos_timestep``                   |             | MIP Convert  | The atmospheric model timestep in integer        | [1]   |
|                                      |             |              | seconds.                                         |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``base_date``                        | MIP Convert | MIP Convert  | The date in the form ``YYYY-MM-DD-hh-mm-ss``.    | [2]   |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``deflate_level``                    |             | MIP Convert  | The deflation level when writing the             |       |
|                                      |             |              | |output netCDF file| from 0 (no compression) to  |       |
|                                      |             |              | 9 (maximum compression).                         |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``hybrid_heights_file``              |             | MIP Convert  | A space separated list of the full path to the   | [3]   |
|                                      |             |              | files containing the information about the       |       |
|                                      |             |              | hybrid heights.                                  |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``mask_slice``                       | MIP Convert | MIP Convert  | Optional slicing expression for masking data     | [4]   |
|                                      |             |              | in the form of ``n:m,i:j``, or ``no_mask``.      |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``model_output_dir``                 | MIP Convert | MIP Convert  | The full path to the root directory containing   | [5]   |
|                                      |             |              | the |model output files|.                        |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``reference_time``                   | MIP Convert | MIP Convert  | The reference time used to construct ``reftime`` |       |
|                                      |             |              | and ``leadtime`` coordinates. Only used if these |       |
|                                      |             |              | coordinates are specified corresponding variable |       |
|                                      |             |              | entries in the |MIP table|                       |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``replacement_coordinates_file``     |             | MIP Convert  | The full path to the |netCDF| file containing    | [6]   |
|                                      |             |              | area variables that refer to the horizontal      |       |
|                                      |             |              | coordinates that should be used to replace the   |       |
|                                      |             |              | corresponding values in the                      |       |
|                                      |             |              | |model output files|.                            |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``run_bounds``                       | MIP Convert | MIP Convert  | The start and end time in the form               |       |
|                                      |             |              | ``<start_time> <end_time>``, where               |       |
|                                      |             |              | ``<start_time>`` and ``<end_time>`` are in the   |       |
|                                      |             |              | form ``YYYY-MM-DD-hh-mm-ss``.                    |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``shuffle``                          |             | MIP Convert  | Whether to shuffle when writing the              |       |
|                                      |             |              | |output netCDF file|.                            |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``sites_file``                       |             | MIP Convert  | The full path to the file containing the         | [7]   |
|                                      |             |              | information about the sites.                     |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+
| ``suite_id``                         | MIP Convert | MIP Convert  | The |suite identifier| of the model.             |       |
+--------------------------------------+-------------+--------------+--------------------------------------------------+-------+

[1] The ``atmos_timestep`` is required for atmospheric tendency diagnostics,
which have |model to MIP mappings| that depend on the atmospheric model
timestep, i.e., the expression contains ``ATMOS_TIMESTEP``.

[2] The ``base_date`` is used to define the units of the time coordinate
in the |output netCDF file| and is specified by the |MIP|.

[3] The file containing the information about the hybrid heights has the
following columns; the ``model level number`` (int), the ``a_value`` (float),
the ``a_lower_bound`` (float), the ``a_upper_bound`` (float), the ``b_value``
(float), the ``b_lower_bound`` (float) and the ``b_upper_bound`` (float).

[4] If not specified, ``mip_convert`` will try to retrieve masking expressions
from plugins (this is a default behaviour for CMIP6-like processing). Putting
``no_mask`` into configuration file allows ``mip_convert`` to process model output
that does not require any masking; custom masks can be specified and passed to
``mip_convert`` without plugins dependencies.

[5] It is expected that the |model output files| are located in the directory
``<model_output_dir>/<suite_id>/<stream_id>/``, where the ``<suite_id>`` is the
|suite identifier| and the ``<stream_id>`` is the |stream identifier|. Note
that MIP Convert will load all the files in this directory and then use the
``run_bounds`` to select the required data; when selecting a short time period
from a large number of |model output files| it is recommended to copy the
relevant files to an empty directory to save time when loading.

[6] Currently, only CICE horizontal coordinates can be replaced.

[7] The file containing the information about the sites has the following
columns; the ``site number`` (int), the ``longitude`` (float, from 0 to 360)
[degrees], the ``latitude`` (float, from -90 to 90) [degrees], the
``orography`` (float) [metres] and a ``comment`` (string).

.. _stream_stream_id:

The ``stream_<stream_id>`` Section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The required :ref:`stream_\<stream_id\> <stream_stream_id>` section, where the
``<stream_id>`` is the |stream identifier|, contains options equal to the name
of the |MIP table| and values equal to a space-separated list of
|MIP requested variable names|. Multiple
:ref:`stream_\<stream_id\> <stream_stream_id>` sections can be defined.

All |output netCDF files| are created for a |stream| before moving onto the
next |stream|.

.. _global_attributes:

The ``global_attributes`` Section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any information provided in the optional
:ref:`global_attributes <global_attributes>` section will be written to the
header of the |output netCDF files|.
