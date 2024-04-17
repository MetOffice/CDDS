# Data Section

The `data` section in the request configuration contains all settings that are used to archive the data in MASS.

## Configuration Values

`data_version`
:   version of the data to archive. Format: `v%Y%m%d`

    **Default:** version of current date

`end_date`
:   end date for the processing.

`start_date`
:   start date for the processing.

`mass_data_class`
:   root of the location of input dataset on MASS, either `crum` or `ens`.

    **Default:** `crum`

`mass_ensemble_member`
:   identifier of the ensemble member for PPE simulations

`model_workflow_id`
:   workflow ID of the simulation model.

`model_workflow_branch`
:   name of the workflow branch of the simulation model.

    **Default:** `cdds`

`model_workflow_revision`
:   workflow revision of the simulation model.

    **Default:** `HEAD`

`streams`
:   restrict only to these streams. If empty, all streams will be processed.

`variable_list_file`
:   path to the user created variables file.

`output_mass_root`
:   full path to the root MASS location to use for archiving the output data, e.g. `moose:/adhoc/users/<user.name>/`

`output_mass_suffix`
:   sub-directory in MASS to use when moving data. This directory is appended to the root mass location defined in `output_mass_root`.

## Examples

!!! example
    ```yaml
    [data]
    data_version = v20240212
    end_date = 2015-01-01T00:00:00Z
    mass_data_class = crum
    mass_ensemble_member = 
    start_date = 1979-01-01T00:00:00Z
    model_workflow_id = u-bp880
    model_workflow_branch = cdds
    model_workflow_revision = HEAD
    streams = ap4 ap5 ap6
    variable_list_file = /home/h03/cdds/variables/variables.txt
    output_mass_root = moose:/adhoc/users/some.user/
    output_mass_suffix = cdds
    ```
