# NetCDF Global Attributes Section

The `netcdf_global_attributes` in the request configuration contains all attributes that will be set in the global attributes 
section of the CMOR file.

## Configuration Values

`attributes`
:   attributes that will be set in the global attributes section of the CMOR file.

## Examples

!!! example
    NetCDF global attributes of a CORDEX experiment:
    ```yaml
    [netcdf_global_attributes]
    driving_experiment = evaluation
    driving_experiment_id = evaluation
    driving_institution_id = MOHC
    driving_source_id = HadREM3-GA7-05
    driving_model_ensemble_member = r1i1p1
    driving_experiment_name = evaluation
    driving_variant_label = r1i1p1f2
    nesting_levels = 1
    rcm_version_id = v1
    project_id = CORDEX-FPSCONV
    domain_id = EUR-11
    domain = Europe
    source_configuration_id = v1.0
    further_info_url = https://furtherinfo.es-doc.org/
    ```
