## Running CDDS

This tutorial serves as a brief introduction to running CDDS by CMORising a short amount of climate data.
Its intention is to provide a minimal example of running CDDS, whilst also signposting some of the other features and capabilities.
There are three main steps to complete.

1. Define the `request.cfg` file and the variables to process.

2. Setup the directory structure.

3. Run the Cylc conversion workflow.


### Configuring the Request

Running CDDS requires the user to appropriately configure a `request.cfg` file (from here on simply referred to as the "request").
This request is provided to many `cdds` commands as a positional argument and contains information ranging from experiment metadata, workflow configuration, ancilary paths, MASS locations, and more.
Each option belongs to a particular section and is documented in [Request Configuration](request/config_request.md).

??? example
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
    mip_table_dir = $CDDS_ETC/mip_tables/GCModelDev/0.0.23
    mode = relaxed
    package = round-1
    workflow_basename = request_id
    root_proc_dir = $SCRATCH/cdds_proc  # A reasonable default for Met Office, change for JASMIN
    root_data_dir = $SCRATCH/cdds_data  # A reasonable default for Met Office, change for JASMIN
    root_ancil_dir = $CDDS_ETC/ancil/
    root_hybrid_heights_dir = $CDDS_ETC/vertical_coordinates/
    root_replacement_coordinates_dir = $CDDS_ETC/horizontal_coordinates/
    sites_file = $CDDS_ETC/cfmip2/cfmip2-sites-orog.txt
    standard_names_version = latest
    standard_names_dir = $CDDS_ETC/standard_names/
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
    model_workflow_revision = not used except with Data Request
    streams = ap5 onm
    variable_list_file = <must be included>
    output_mass_root = moose:/adhoc/users/<moose user id>  # Update with user id
    output_mass_suffix = testing  # This is appended to output_mass_root
    
    [misc]
    atmos_timestep = 1200  # This is model dependent
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
    cylc_args = -v
    no_email_notifications = True
    scale_memory_limits = 
    override_cycling_frequency = 
    model_params_dir = 
    continue_if_mip_convert_failed = False
    ```

For simplicity this tutorial relies on many of the default values, and eliminates unused options to reduce the request to its most minimal form.
The highlighted lines indicate those that the user may need to modify to run this example.

=== "Met Office"

    ```ini hl_lines="20 21 29 30"
    [metadata]
    branch_method = no parent
    base_date = 1850-01-01T00:00:00Z
    calendar = 360_day
    experiment_id = my-experiment-id
    institution_id = MOHC
    license = GCModelDev model data is licensed under the Open Government License v3 (https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
    mip = MOHCCP
    mip_era = GCModelDev
    sub_experiment_id = none
    variant_label = r1i1p1f3
    model_id = HadGEM3-GC31-LL
    model_type = AOGCM AER

    [common]
    mip_table_dir = $CDDS_ETC/mip_tables/GCModelDev/0.0.23
    mode = relaxed
    package = round-1
    workflow_basename = request_id
    root_proc_dir = $DATADIR/cdds_quickstart_tutorial/proc
    root_data_dir = $DATADIR/cdds_quickstart_tutorial/data

    [data]
    end_date = 1955-01-01T00:00:00Z
    mass_data_class = crum
    start_date = 1950-01-01T00:00:00Z
    model_workflow_id = u-bg466
    streams = ap5
    variable_list_file = $DATADIR/cdds_quickstart_tutorial/variables.txt
    output_mass_root = moose:/adhoc/users/<moose user id>
    output_mass_suffix = quickstart

    [conversion]
    skip_extract = False
    skip_extract_validation = False
    skip_configure = False
    skip_qc = False
    skip_archive = False
    ```

=== "JASMIN"

    ```ini hl_lines="20 21 29 30 39"
    [metadata]
    branch_method = no parent
    base_date = 1850-01-01T00:00:00Z
    calendar = 360_day
    experiment_id = my-experiment-id
    institution_id = MOHC
    license = GCModelDev model data is licensed under the Open Government License v3 (https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
    mip = MOHCCP
    mip_era = GCModelDev
    sub_experiment_id = none
    variant_label = r1i1p1f3
    model_id = HadGEM3-GC31-LL
    model_type = AOGCM AER

    [common]
    mip_table_dir = $CDDS_ETC/mip_tables/GCModelDev/0.0.23
    mode = relaxed
    package = round-1
    workflow_basename = request_id
    root_proc_dir = $DATADIR/cdds_quickstart_tutorial/proc
    root_data_dir = $DATADIR/cdds_quickstart_tutorial/data

    [data]
    end_date = 1955-01-01T00:00:00Z
    mass_data_class = crum
    start_date = 1950-01-01T00:00:00Z
    model_workflow_id = u-bg466
    streams = ap5
    variable_list_file = $DATADIR/cdds_quickstart_tutorial/variables.txt

    [conversion]
    skip_extract = True
    skip_extract_validation = True
    skip_configure = False
    skip_qc = False
    skip_archive = True
    jasmin_account =
    ```

1. Create a working directory for the `request.cfg`, and the `proc` and `data` directories.
   It doesn't have to be the same as those used in the following example, just be sure to update the `request.cfg` appropriately. 
   ```
   cd $DATADIR
   mkdir cdds_quickstart_tutorial
   cd cdds_quickstart_tutorial
   mkdir proc data
   touch request.cfg
   ```
   Also, it isn't a requirement to have the `request.cfg` in the same directory as the `proc` and `data` directories.
2. Copy the above example `request.cfg` into your empty `request.cfg` file.
3. Update fields in the `request.cfg`.
    1. If you are using a different path to `$DATADIR/cdds_quickstart_tutorial` update the `root_proc_dir`, `root_data_dir`, and `variable_list_file` fields.
    1. If you are on Azure, update the `output_mass_root` with your MASS username.
    1. If you are on JASMIN, make sure you populate the `jasmin account` field with an appropriate account (used for LOTUS2).
5. Create an empty `variables.txt` file and add the following line.
   ```
   Amon/tas:ap5
   ```
6. Activate the CDDS environment 
   ```bash
   source ~cdds/bin/setup_env_for_cdds 3.1.2
   ```
7. Validate the `request.cfg`.
   ```
   validate_request request.cfg
   ```
   If any errors are reported and you are not able to please contact the CDDS team for help.


### Preparing for Processing

The following commands assume we are in the working directory created previously containing the `request.cfg` and that a CDDS environment is activated.

Run the following command.

```
cdds_create_cdds_directories request.cfg
```

??? info

    This will use the `root_proc_dir` and `root_data_dir` paths within the request to create the following directory structures.
    The `proc` directory holds the log files created by the different `cdds` commands.
    The `data` directory will home the input model data e.g. `.pp` files as well as the output CMORised `.nc` output.

    The proc directory is made up of a nested directory structure.

    ```
    proc
    └── GCModelDev
        └── MOHCCP
            └── request_id
                └── round-1
                    ├── archive
                    ├── configure
                    ├── convert
                    ├── extract
                    ├── prepare
                    └── qualitycheck
    ```
    A similar hierarchical structure is created for all

    ```
    data
    └── GCModelDev
        └── MOHCCP
            └── HadGEM3-GC31-LL
                └── my-experiment-id
                    └── r1i1p1f3
                        └── round-1
                            ├── input
                            │   └── u-bg466
                            └── output
    ```


Run the following command.

```
prepare_generate_variable_list request.cfg
```

??? info

    This takes the user variables file provided by the `variable_list_file` option, and creates an internally used `.json` version which includes additional metadata.
    The file can be found in the `prepare` proc sub-directory.
    ```
    proc/GCModelDev/MOHCCP/request_id/round-1/prepare/GCModelDev_MOHCCP_my-experiment-id_HadGEM3-GC31-LL.json
    ```
    
    

    ```json
    {
      "checksum":"md5: 89a430535551e97433fd8a22edcfec24",
      "experiment_id":"my-experiment-id",
      "history":[
        {
          "comment":"Requested variables file created.",
          "time":"2025-05-07T07:40:21.049522"
        }
      ],
      "metadata":{},
      "mip":"MOHCCP",
      "mip_era":"GCModelDev",
      "model_id":"HadGEM3-GC31-LL",
      "model_type":"AOGCM AER",
      "production_info":"Produced using CDDS Prepare version \"3.1.2\"",
      "requested_variables":[
        {
          "active":true,
          "cell_methods":"area: time: mean",
          "comments":[],
          "dimensions":[
            "longitude",
            "latitude",
            "time",
            "height2m"
          ],
          "frequency":"mon",
          "in_mappings":true,
          "in_model":true,
          "label":"tas",
          "miptable":"Amon",
          "producible":"yes",
          "stream":"ap5"
        }
      ],
      "status":"ok",
      "suite_branch":"cdds",
      "suite_id":"u-bg466",
      "suite_revision":"HEAD"
    ```

### Running the Conversion Workflow

=== "Met Office"
    If there were no errors running the previous command then it should be simply a case of running this final command.
    ```
    cdds_convert request.cfg
    ```

=== "JASMIN"

    Until a LOTUS2 partition that provides MASS access is made available, the `cdds_extract` command must be run manually by the user.
    Before running the command you must ssh into the MASS server using the following command.
    ```
    ssh <user>@mass-cli.jasmin.ac.uk
    ```
    You may need to reactivate the CDDS environment, once done you can run extract with.
    ```
    cdds_extract request.cfg
    ```
    Once this command has completed you will then need to ssh into the Cylc server
    ```
    cdds_convert request.cfg
    ```

The `cdds_convert` command does several things when run.

- Generates the `mip_convert` template files.
- Makes a copy of the conversion workflow.
- Populates various Jinja2 template variables.
- Automatically submits the workflow using `cylc vip`.

Once the `cdds_convert` command has completed you should be able to monitor your running workflow using `cylc tui` or `cylc gui`.


## Useful Configuration Options

What follows are some examples of options that are useful to be aware of but the list is not exhaustive.
The full list of configuration options available in the request can be found in the [Request Configuration](request/config_request.md) tutorial.


### Adding More Variables

To process more variables you will first need to add the appropriate entry to the `variables.txt`.

```
<mip table>/<variable name>:<stream>
```

If you have

```bash
stream_mappings
```

### Relaxed Mode

The example `request.cfg` configuration given above runs.
By changing the mode to `relaxed` this allows the user to provide arbitrary metadata values that do not exist in the CV's.
This is particularly useful for model development work.

```ini
[common]
mode = relaxed
```

### Global Attributes

Arbitrary netcdf global attributes can be added to the CMORised files using the following 

```ini
[netcdf_global_attributes]
ensemble = 
```
