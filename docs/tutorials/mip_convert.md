## Overview

The [`mip_convert`](https://github.com/MetOffice/CDDS/blob/main/mip_convert) package enables a user to produce the output netCDF files for a MIP using model output files.

``` mermaid
graph LR
  A[model output .pp data] --> C[MIP Convert + CMOR];
  B[model output .nc data] --> C;
  C --> D[CF/CMIP6 Compliant .nc data];
```  

1. The user makes requests for one or more MIP requested variables by providing specific information (including the appropriate MIP requested variable names) in the user configuration file.
2. The information required to produce the MIP requested variables is gathered from the user configuration file, the model to MIP mapping configuration files and the appropriate MIP table, in that order.
3. The following steps are then performed for each MIP requested variable name in the user configuration file to produce the output netCDF files:
    1. load the relevant data from the model output files into one or more input variables depending on whether there is a one-to-one / simple arithmetic relationship between the MIP output variable and the input variables or if the MIP output variable is based on an arithmetic combination of two or more input variables, respectively, using Iris and the information provided in the user configuration file and the model to MIP mapping configuration files.
    2. process the input variable / input variables to produce the MIP output variable using the information provided in the model to MIP mapping configuration files.
    3. save the MIP output variable to an output netCDF file using CMOR and the information provided in the user configuration file and the appropriate MIP table.

### Recommended Reading

- The [Design Considerations and Overview](https://cmor.llnl.gov/#design-considerations-and-overview) section in the CMOR Documentation.


## Quick Start Guide

1. Download the template user configuration file [`mip_convert.cfg`](https://github.com/MetOffice/CDDS/blob/main/mip_convert/etc/mip_convert.cfg).

2. Make the appropriate edits to the template user configuration file using the information provided in the "User Configuration File" section and the specified sections in the [CMOR Documentation](https://cmor.llnl.gov/).

3. Source an environment with `cdds` and verify that `mip_convert` runs.
    ```bash
    mip_convert -h
    ```

4. Produce the output netCDF files by running `mip_convert` and passing in the modified user configuration file as an argument.
    ```bash
    mip_convert mip_convert.cfg
    ```

5. Check the exit code
    ```bash
    echo $?
    ```

    | Exit Code | Meaning          |
    |-----------|------------------|
    | 0         | No errors were raised during processing.                                              |
    | 1         | An exception was raised and no MIP requested variables were produced.                 |
    | 2         | One or more MIP requested variables were produced but not *all* variables were produced. See the ``CRITICAL`` messages in the log for further information about the MIP requested variables not produced.                                         |

6. Check that the output netCDF files are as expected.
    For help or to report an issue, please see `support`.


### Selected MIP Convert Arguments

| <div style="width:195px">Argument</div>                          | Description    |
|-----------------------------------|----------------|
| `config_file`                     | The name of the user configuration file. For more information, please see the MIP Convert user guide |
| `-s` or `--stream_identifiers`    | The stream identifiers to process. If all streams should be processed, do not specify this option. |
| `--relaxed-cmor`                  | If specified, CMIP6 style validation is not performed by CMOR. If the  validation is run then the following fields are not checked; `model_id` (`source_id`),    `experiment_id`, `further_info_url`, `grid_label`, `parent_experiment_id`, `sub_experiment_id`.  |
| `--mip_era`                       | The MIP era (e.g. CMIP6). |
| `--external_plugin`               | Module path to external CDDS plugin (e.g. `arise.plugin`) |
| `--external_plugin_location`      | Path to the external plugin implementation   (e.g. `/project/cdds/arise`) |

### Example Usage

!!! example "Run for all streams with full checking of metadata"
    ```bash
    mip_convert mip_convert.cfg
    ```

!!! example "Run for a single stream in relaxed mode"
    ```bash
    mip_convert mip_convert.cfg -s ap4 --relaxed_cmor
    ```


## User Configuration File Reference

The user configuration file provides the information required by MIP Convert to produce the output netCDF files.
It contains the following sections, some of which are optional.

| Section                | Summary                                                   |
|------------------------|-----------------------------------------------------------|
| `[COMMON]`             | Convenience for setting up shared config values.          |
| `[cmor_setup]`         | Passed through to CMOR's `cmor_setup()` routine.          |
| `[cmor_dataset]`       | Passed through to CMOR's `cmor_data_set_json()` routine.  |
| `[request]`            | Configure `mip_convert` including input data.             |
| `[stream_<stream_id>]` | The variables to produce from a particular `<stream_id>`. |
| `[masking]`            | Apply polar row masking if needed.                        |
| `[halo_removal]`       | Apply stripping of halo columns and rows if needed.       |
| `[global_attributes]`  | Add global attributes to the output netCDF.               |


### **COMMON**

The optional `[COMMON]` section.

### **cmor_setup**

The `[cmor_setup]` section contains the following options which are used by `cmor_setup()`.
For a description of each option please see the documentation for [cmor_setup()](https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_setup).

|          Option           | Required by |   Used by             | CMOR Name    |
|---------------------------|-------------|-----------------------|--------------|
| ``mip_table_dir``         | MIP Convert | CMOR + MIP Convert    | `inpath`     |
| ``netcdf_file_action``    |             | CMOR                  |              |
| ``set_verbosity``         |             | CMOR                  |              |
| ``exit_control``          |             | CMOR                  |              |
| ``cmor_log_file``         |             | CMOR                  | `log_file`   |
| ``create_subdirectories`` |             | CMOR                  |              |

!!! tip
    When configuring a user configuration file, the `mip_table_dir` is likely to be the only value that will need modification.


### **cmor_dataset**

The required `cmor_dataset` section contains the following options used for [cmor_data_set_json()](https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_dataset_json)

|              Option             | Required by        |          Used by   | Notes   |
|---------------------------------|--------------------|--------------------|---------|
| ``branch_method``               | MIP Convert + CMOR | MIP Convert + CMOR | [1]     |
| ``calendar``                    | MIP Convert + CMOR | MIP Convert + CMOR | [2]     |
| ``comment``                     |                    | CMOR               | [1] [3] |
| ``contact``                     |                    | CMOR               | [1]     |
| ``experiment_id``               | MIP Convert + CMOR | MIP Convert + CMOR | [1]     |
| ``grid``                        | CMOR               | CMOR               | [1]     |
| ``grid_label``                  | CMOR               | CMOR               | [1]     |
| ``institution_id``              | MIP Convert + CMOR | MIP Convert + CMOR | [1]     |
| ``license``                     | CMOR               | CMOR               | [1]     |
| ``mip``                         | CMOR               | CMOR               | [1] [4] |
| ``mip_era``                     | MIP Convert + CMOR | MIP Convert + CMOR | [1]     |
| ``model_id``                    | MIP Convert + CMOR | MIP Convert + CMOR | [1] [5] |
| ``model_type``                  | CMOR               | CMOR               | [1] [6] |
| ``nominal_resolution``          | CMOR               | CMOR               | [1]     |
| ``output_dir``                  | MIP Convert + CMOR | MIP Convert + CMOR | [7]     |
| ``output_file_template``        |                    | CMOR               |         |
| ``output_path_template``        |                    | CMOR               |         |
| ``references``                  |                    | CMOR               | [1]     |
| ``sub_experiment_id``           | MIP Convert + CMOR | MIP Convert        | [1]     |
| ``variant_info``                |                    | CMOR               | [1]     |
| ``variant_label``               | MIP Convert + CMOR | MIP Convert + CMOR | [1]     |

**Notes**

1. For a description of each option, please see the `CMIP6 Global Attributes document`_.
1. See calendars for allowed values.
1. It is recommended to use the ``comment`` to record any perturbed physicsdetails.
1. See MIP.
1. See model identifier.
1. See model type.
1. See ``outpath`` in the documentation for `cmor_dataset_json`_.

MIP Convert determines:

* the ``experiment``, ``institution``, ``source``, ``sub_experiment`` from the CV file using the ``experiment_id``, ``institution_id``, ``source_id`` and ``sub_experiment_id``, respectively
* the ``forcing_index``, ``initialization_index``, ``physics_index`` and ``realization_index`` from the ``variant_label``
* the ``further_info_url`` and ``tracking_prefix`` based on the information from the CV file
* the ``history``

!!! info "Whenever a parent experiment exists the following options must also be specified."

    |              Option             |     Used by     |   Notes   |
    |---------------------------------|-----------------|-----------|
    | ``branch_date_in_child``        | MIP Convert     | [1][2][3] |
    | ``branch_date_in_parent``       | MIP Convert     | [1][2][3] |
    | ``parent_base_date``            | MIP Convert     | [1][2]    |
    | ``parent_experiment_id``        | CMOR            | [3]       |
    | ``parent_mip_era``              | CMOR            | [3]       |
    | ``parent_model_id``             | CMOR            | [3][4]    |
    | ``parent_time_units``           | CMOR            | [3]       |
    | ``parent_variant_label``        | CMOR            | [3]       |
    
    **Notes**
    
    1. CMOR requires ``branch_time_in_child`` and ``branch_time_in_parent``, which is determined from the options ``base_date`` (see the `request <request_section>` section) / ``parent_base_date`` (the base date of the ``child_experiment_id`` / ``parent_experiment_id``) and ``branch_date_in_child`` / ``branch_date_in_parent`` (the date in the ``child_experiment_id`` / ``parent_experiment_id`` from which the experiment branches) from the `cmor_dataset <cmor_dataset_section>` section in the |user configuration file| by taking the difference (in days) between the ``branch_date_in_child`` / ``branch_date_in_parent`` and the ``base_date`` / ``parent_base_date``. If ``branch_date_in_child`` or ``branch_date_in_parent`` is ``N/A`` then ``branch_time_in_parent`` is set to 0.
    2. Dates should be provided in the form `YYYY-MM-DDThh:mm:ssZ`.
    3. For a description of each option, please see the [CMIP6 Global Attributes document](https://docs.google.com/document/d/1h0r8RZr_f3-8egBMMh7aqLwy3snpD6_MrDz1q8n5XUk).
    4. See ``parent_source_id`` in the [CMIP6 Global Attributes document](https://docs.google.com/document/d/1h0r8RZr_f3-8egBMMh7aqLwy3snpD6_MrDz1q8n5XUk).
    
    
### **request**

The required `request` section contains the following options which are used only by MIP Convert.

| <div style="width:125px">Option</div> | Required | Description                                                                                                                                                                            | Notes |
|---------------------------------------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| `ancil_files`                         |          | A space separated list of the full paths to any required ancillary files.                                                                                                              |       |
| `atmos_timestep`                      |          | The atmospheric model timestep in integer seconds.                                                                                                                                     | [1]   |
| `base_date`                           | Yes      | The date in the form `YYYY-MM-DDThh:mm:ss`.                                                                                                                                            | [2]   |
| `deflate_level`                       |          | The deflation level when writing the output netCDF file from 0 (no compression) to 9 (maximum compression).                                                                            |       |
| `force_coordinate_rotation`                      |          | Whether to rotate the coordination system if it is not already rotated.                                                                                                                |       |
| `hybrid_heights_file`                 |          | A space separated list of the full path to the files containing the information about the hybrid heights.                                                                              | [3]   |
| `mask_slice`                          | Yes      | Optional slicing expression for masking data in the form of `n:m,i:j`, or `no_mask`                                                                                                    | [4][8]   |
| `model_output_dir`                    | Yes      | The full path to the root directory containing the model output files.                                                                                                                 | [5]   |
| `reference_time`                      | Yes      | The reference time used to construct `reftime` and `leadtime` coordinates. Only used if these coordinates are specified corresponding variable entries in the MIP table                |       |
| `replacement_coordinates_file`        |          | The full path to the netCDF file containing area variables that refer to the horizontal coordinates that should be used to replace the corresponding values in the model output files. | [6]   |
| `run_bounds`                          | Yes      | The start and end time in the form `<start_time> <end_time>`, where `<start_time>` and `<end_time>` are in the form `YYYY-MM-DDThh:mm:ss`.                                             |       |
| `shuffle`                             |          | Whether to shuffle when writing the output netCDF file.                                                                                                                                |       |
| `sites_file`                          |          | The full path to the file containing the information about the sites.                                                                                                                  | [7]   |
| `suite_id`                            | Yes      | The suite identifier of the model.                                                                                                                                                     |       |

**Notes**

1. The ``atmos_timestep`` is required for atmospheric tendency diagnostics, which have model to MIP mappings that depend on the atmospheric model timestep, i.e., the expression contains ``ATMOS_TIMESTEP``.
1. The ``base_date`` is used to define the units of the time coordinate in the output netCDF file and is specified by the MIP.
1. The file containing the information about the hybrid heights has the following columns;
    1. the ``model level number`` (int)
    1. the ``a_value`` (float)
    1. the ``a_lower_bound`` (float)
    1. the ``a_upper_bound`` (float)
    1. the ``b_value`` (float)
    1. the ``b_lower_bound`` (float)
    1. the ``b_upper_bound`` (float)
1. If not specified, ``mip_convert`` will try to retrieve masking expressions from plugins (this is a default behaviour for CMIP6-like processing). Putting ``no_mask`` into configuration file allows ``mip_convert`` to process model output that does not require any masking; custom masks can be specified and passed to ``mip_convert`` without plugins dependencies.
1. It is expected that the model output files are located in the directory ``<model_output_dir>/<suite_id>/<stream_id>/``, where the ``<suite_id>`` is the suite identifier and the ``<stream_id>`` is the |stream identifier|. Note that MIP Convert will load all the files in this directory and then use the ``run_bounds`` to select the required data; when selecting a short time period from a large number of |model output files| it is recommended to copy the relevant files to an empty directory to save time when loading.
1. Currently, only CICE horizontal coordinates can be replaced.
1. The file containing the information about the sites has the following columns;
    1. the ``site number`` (int)
    1. the ``longitude`` (float, from 0 to 360) [degrees]
    1. the ``latitude`` (float, from -90 to 90) [degrees]
    1. the ``orography`` (float) [metres] and a ``comment`` (string).
1. This is usually only used to mask ocean/seaice data as part of a CDDS run.

### **stream_<\stream_id>**

The required `[stream_<stream_id>]` section, where the ``<stream_id>`` is the stream identifier, contains options equal to the name of the MIP table and values equal to a space-separated list of MIP requested variable names.
Multiple `[stream_<stream_id>]` sections can be defined.

!!! note 
    All output netCDF files are created for a stream before moving onto the next stream.

!!! example
    If we wanted to produce the following variables `Amon/tas`, `Amon/pr`, `Emon/ps`, `Amon/tasmax`, `day/tasmin` using the `CMIP6` tables.

    1. We need two `stream_stream_id` sections as the list of MIP requested variables span streams `ap5` and `ap6`.
    2. Within each of these sections we specify the mip table in the form `<MIP_ERA>_<MIP_TABLE>:`
    3. Then the list of variables names as a space seperated list.

    ```config
    [stream_ap5]
    CMIP6_Amon: tas pr
    CMIP6_Emon: ps
    
    [stream_ap6]
    CMIP6_Amon: tasmax
    CMIP6_day: tasmin
    ```


### **masking**

The optional `masking` section is used if a particular stream needs to be masked.
This is usually only used for polar row masking in NEMO & CICE output

!!! example
    ```config
    [masking]
    stream_inm_cice-T: -1:,180:
    ```

### **halo_removal**

The optional `halo removal` section is used if for a particular stream haloes are to be removed.

!!! example
    ```config
    [halo_removal]
    stream_apa: 5:,:-10
    stream_ap6: 20:-15
    ```


### **global_attributes**

The optional `global_attributes` section.
Any information provided in the optional `global_attributes <global_attributes>` section will be written to the header of the output netCDF files.
