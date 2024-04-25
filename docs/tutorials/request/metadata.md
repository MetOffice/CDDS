# Metadata Section

The `metadata` section in the request configuration contains all metadata settings about the experiment that should be 
processed.

## Configuration Values

`branch_method`
:   branching procedure - `standard`, `continuation` or `no parent`

`base_date`
:   used to define the units of the time coordinate in the netCDF file.
    *Format:* `yyyy-mm-ddTHH:MM:SSZ`, e.g. `1850-01-01T00:00:00Z`

    **Default:** `1850-01-01T00:00:00Z`

`calendar`
:   that should be used - `360_day` or `gregorian`

`experiment_id`
:   experiment identifier

`institution_id`
:   institution identifier, e.g. `MOHC` for `Met Office Hadley Centre`

`license`
:   license restrictions. It ensures that anyone using the files has access to the terms of use.

    **Default:** The licenses that the corresponding plugin is provided for the given MIP era.

`mip`
:   the model intercomparison project, e.g. `ScenarioMIP`

`mip_era`
:   the associated cycle, e.g. `CMIP6`, `GCDevModel`, `CORDEX`

`sub_experiment_id`
:   identifier of the sub experiment. For example, it is needed for CMIP6 hindcast or forecast experiments to indicate 
    start year. If no sub experiment is given, set it to `none`

    **Default:** `none`

`variant_label`
:   the label of the variant of the experiment that should be considered.

`model_id`
:   a short name identifying the model, also know as `source_id`, e.g. `HadGEM3-GC31-LL`.

`model_type`
:   a text code identifying which model components are used in the given experiments separated by white spaces, 
    e.g. `AOGCM AER BGC`


### Configuration values for parent experiment

Following configuration values are only needed to be set if the `branch_method` is `standard` or `continuation`:

`branch_date_in_child`
:   branch data with respect to child's time axis. 
    *Format:* `yyyy-mm-ddTHH:MM:SSZ`, e.g. `1990-01-01T00:00:00Z`

`branch_date_in_parent`
:   branch date with respect to parent time axis
    *Format:* `yyyy-mm-ddTHH:MM:SSZ`, e.g. `2000-01-01T00:00:00Z`

`parent_base_date`
:   used to define the units of the time coordinate in the netCDF files. 
    *Format:* `yyyy-mm-ddTHH:MM:SSZ`, e.g. `2005-01-01T00:00:00Z`

    **Default:** `1850-01-01T00:00:00Z`

`parent_experiment_id`
:   parent experiment identifier, e.g. `piControl`

`parent_mip`
:   the model intercomparison project of the parent experiment

`parent_mip_era`
:   parent's associated MIP cycle, e.g. `CMIP6`

`parent_model_id`
:   a short name identifying the parent model, e.g. `HadGEM3-GC31-LL`.

    **Default**: The same model ID of the experiment that should be processed

`parent_time_units`
:   the time units used in the parent experiment.

    **Default:** `days since 1850-01-01`

`parent_variant_label`
:   the label of the specific variant of the parent experiment that should be considered.


## Examples

!!! example "CIMP6 experiment without parent"
    ```yaml
    [metadata]
    branch_method = no parent
    calendar = 360_day
    experiment_id = amip
    institution_id = MOHC
    license = CMIP6 model data produced by MOHC is licensed under a Creative 
              Commons Attribution ShareAlike 4.0 International License
    mip = CMIP
    mip_era = CMIP6
    sub_experiment_id = none
    variant_label = r1i1p1f4
    model_id = UKESM1-0-LL
    model_type = AGCM AER CHEM
    standard_names_version = latest
    standard_names_dir = /home/h03/cdds/etc/standard_names
    ```

!!! example "CMIP6 experiment with parent"
    ```yaml
    [metadata]
    branch_date_in_child = 1850-01-01T00:00:00Z
    branch_date_in_parent = 2250-01-01T00:00:00Z
    branch_method = standard
    child_base_date = 1850-01-01T00:00:00Z
    calendar = 360_day
    experiment_id = historical
    institution_id = MOHC
    license = CMIP6 model data produced by MOHC is licensed under a Creative 
              Commons Attribution ShareAlike 4.0 International License.
    mip = CMIP
    mip_era = CMIP6
    parent_base_date = 1850-01-01T00:00:00Z
    parent_experiment_id = piControl
    parent_mip = CMIP
    parent_mip_era = CMIP6
    parent_model_id = UKESM1-0-LL
    parent_time_units = days since 1850-01-01
    parent_variant_label = r1i1p1f2
    sub_experiment_id = none
    variant_label = r1i1p1f2
    standard_names_version = latest
    standard_names_dir = /home/h03/cdds/etc/standard_names/
    model_id = UKESM1-0-LL
    model_type = AOGCM BGC AER CHEM
    ```