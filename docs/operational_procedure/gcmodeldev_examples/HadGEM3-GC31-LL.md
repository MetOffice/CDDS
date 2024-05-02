# GCModelDev HadGEM3 GC31 LL request file example

## CDDS v3.0.0

In CDDS v3.0.0 the request file format was changed from `json` to `ini`.

```ini
[metadata]
branch_date_in_child = 
branch_date_in_parent = 
branch_method = no parent
base_date = 1850-01-01T00:00:00Z
calendar = 360_day
experiment_id = my-experiment-id
institution_id = MOHC
license = GCModelDev model data is licensed under the Open Government License v3 (https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
mip = MOHCCP
mip_era = GCModelDev
parent_base_date = 1850-01-01T00:00:00Z
parent_experiment_id = 
parent_mip = 
parent_mip_era = 
parent_model_id = HadGEM3-GC31-LL
parent_time_units = days since 1850-01-01
parent_variant_label = 
sub_experiment_id = none
variant_label = r1i1p1f3
model_id = HadGEM3-GC31-LL
model_type = AOGCM AER

[netcdf_global_attributes]

[common]
external_plugin = 
external_plugin_location = 
mip_table_dir = /home/h03/cdds/etc/mip_tables/GCModelDev/0.0.9
mode = relaxed
package = round-1
workflow_basename = request_id
root_proc_dir = 
root_data_dir = 
root_ancil_dir = /home/h03/cdds/etc/ancil/
root_hybrid_heights_dir = /home/h03/cdds/etc/vertical_coordinates/
root_replacement_coordinates_dir = /home/h03/cdds/etc/horizontal_coordinates/
sites_file = /home/h03/cdds/etc/cfmip2/cfmip2-sites-orog.txt
standard_names_version = latest
standard_names_dir = /home/h03/cdds/etc/standard_names/
simulation = False
log_level = INFO

[data]
data_version =  
end_date = 2015-01-01T00:00:00Z
mass_data_class = crum
mass_ensemble_member = 
start_date = 1950-01-01T00:00:00Z
model_workflow_id = u-bg466
model_workflow_branch = trunk
model_workflow_revision = not used except with data request
streams = ap5 onm
variable_list_file = 
output_mass_root = 
output_mass_suffix = 

[misc]
atmos_timestep = 1200
use_proc_dir = True
no_overwrite = False

[inventory]
inventory_check = False
inventory_database_location = 

[conversion]
skip_extract = False
skip_extract_validation = False
skip_configure = False
skip_qc = False
skip_archive = False
cdds_workflow_branch = trunk
cylc_args = -v
no_email_notifications = True
scale_memory_limits = 
override_cycling_frequency = 
model_params_dir = 
continue_if_mip_convert_failed = False
```
