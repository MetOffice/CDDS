## Running the Climate Data Dissemination System

This tutorial serves as a brief introduction to running CDDS by CMORising a small amount of climate data.
Its intention is to provide a minimal example of running CDDS, whilst also sign posting some of the other features and capabilities.
The entire process can be roughly split into three parts.

1. Define the `request.cfg` file and the variables to process.

2. Setup the directory structure.

3. Run the Cylc conversion workflow.

!!! warning "Prerequisites"

    This guide does assume that you can run `cylc` workflows and that you have access to `mass`.


### Configuring the Request

Running CDDS requires the user to appropriately configure a `request.cfg` file (from here on simply referred to as the "request").
This request is provided to many `cdds` commands as a positional argument and contains information ranging from experiment metadata, workflow configuration, ancilary paths, MASS locations, and more.
Each option belongs to a particular section and is documented in [Request Configuration](request/config_request.md).

??? example "An Explicit Request Example Including Unused Fields"
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
Below two example requests are provided, one for use at the Met Office and other on JASMIN.
The highlighted lines in each request indicate fields that the user may need to modify to run this example successfully.

=== "Met Office request.cfg"

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

=== "JASMIN request.cfg"

    ```ini hl_lines="20 21 29 37"
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

!!! question "What is GCModelDev?"

    You may notice in the above request examples that the `metadata` section references `GCModelDev` (and other non-CMIP6 terms), rather than CMIP6.
    The `GCModelDev` project is an informal duplication of the CMIP6 Controlled Vocabulary and MIP tables that helps facilitate ad-hoc CMORisation for activities such as model development (you can find the soon to be made public Github repository [here](https://github.com/MetOffice/gcmodeldev-cmor-tables)).
    It allows for extra variables to be added in addition to the standard MIP tables, as well as new models and experiments.
    The basic principles of running CDDS remain the same whether you are using GCModelDev or CMIP6.

1. Create a working directory for the `request.cfg`, and the `proc` and `data` directories.
   It doesn't have to be the same as those used in the following example, just be sure to update the `request.cfg` appropriately. 
   ```
   cd $DATADIR
   mkdir cdds_quickstart_tutorial
   cd cdds_quickstart_tutorial
   mkdir proc data
   touch request.cfg
   ```
   Note that it isn't a requirement to have the `request.cfg` in the same directory as the `proc` and `data` directories.
2. Copy the above example `request.cfg` into your empty `request.cfg` file.
3. Update fields in the `request.cfg`.
    1. If you are using a different path to `$DATADIR/cdds_quickstart_tutorial` update the `root_proc_dir`, `root_data_dir`, and `variable_list_file` fields.
    1. If you are on Azure, update the `output_mass_root` with your MASS username.
    1. If you are on JASMIN populate the `jasmin_account` field with an appropriate account name (used for job submission, see JASMIN docs [here](https://help.jasmin.ac.uk/docs/batch-computing/how-to-submit-a-job/#new-slurm-job-accounting-hierarchy)).
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
   If any errors are reported and you are not able to fix please contact the CDDS team for help.


### Preparing for Processing

The following commands assume you are in the working directory created previously containing the `request.cfg`, and that the CDDS environment is activated.

1. Create the directory structure for storing the log and data files created during processing.

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


2. Create the internal variables list used by `cdds`.

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

    1. Launch the `cylc` conversion workflow.
        ```
        cdds_convert request.cfg
        ```

=== "JASMIN"

    1. Until a LOTUS2 MASS partition  is available the `cdds_extract` command must be run manually rather than within the workflow.
        To access `mass` on JASMIN `ssh` into the MASS `mass-cli.jasmin.ac.uk` server.
        ```
        ssh <username>@mass-cli.jasmin.ac.uk
        ```
    2. Reactivate the CDDS environment.
        ```bash
        source /home/users/cdds/bin/setup_env_for_cdds 3.1.2
        ```
    3. You can then run extract. (Not applicable to this example, but if you are processing multiple streams then these must be done individually e.g. `cdds_extract request.cfg -s ap5; cdds_extract request.cfg -s onm`)
        ```
        cdds_extract request.cfg
        ```
    4. Once this command has completed you will then need to `ssh` into the Cylc server
        ```
        exit
        ssh <username>@cylc2.jasmin.ac.uk -XYA
       ```
    5. Reactivate the CDDS environment.
        ```bash
        source /home/users/cdds/bin/setup_env_for_cdds 3.1.2
        ```
    6. Launch the `cylc` conversion workflow.
       ```
       cdds_convert request.cfg
       ```

The `cdds_convert` command does several things when run.

- Generates the `mip_convert` template files.
- Makes a copy of the conversion workflow.
- Populates various Jinja2 template variables.
- Automatically submits the workflow using `cylc vip`.

Once the `cdds_convert` command has completed you can monitor the running workflow using `cylc tui` or `cylc gui`.

### Inspecting Your Data

When the workflow has completed successfully you can inspect the CMORised data.
On disk the CMORised output can be found by descending the `root_data_dir` directory until the until reaching the `output` directory.

```
$DATADIR/cdds_quickstart_tutorial/data/GCModelDev/MOHCCP/HadGEM3-GC31-LL/my-experiment-id/r1i1p1f3/round-1/output
```

Within this directory you will find the following hierarchy.
The `<stream>_concat` and `<stream>_mip_convert` directories are only used during processing and do not contain 

```
├── <stream>
│   └── <MIP Table>
│       └── <variable>
│           └── <file(s)>
```

If you are running the example at the Met Office and you did *not* switch off archiving (e.g. `skip_archive = True`), then the CMORised output will also have been archived to `mass`.
This will be stored in a location based on the request fields `output_mass_root` `output_mass_suffix` e.g., `moo ls moose:/adhoc/users/<username>/quickstart`.


## Adapting the Request

If you are wanting to CMORise data for publication then you should follow the relevant Operational Procedure.


## Useful Configuration Options

What follows are some examples of options that are useful to be aware of but the list is not exhaustive.
The full list of configuration options available in the request can be found in the [Request Configuration](request/config_request.md) tutorial.


### Adding More Variables

To process more variables you will first need to add the appropriate entry to the `variables.txt`.

```
<mip table>/<variable name>:<stream>
```

If you have the CMIP6 STASH configuration then you can use the `stream_mappings` command to add the stream field to each line for CMIP6 variables that CDDS has information for.

```bash
stream_mappings
```

### Relaxed and Strict Modes

The example `request.cfg` configuration given in this tutorial runs in "relaxed" mode.
This allows the user to provide arbitrary metadata values that do not exist in the Controlled Vocabulary, and is particularly useful for model development work.
If you want to ensure that the metadata is consistent with the Controlled Vocabulary you must change the mode to `strict`.

```ini
[common]
mode = strict
```

### Global Attributes

Arbitrary netcdf global attributes can be added to the CMORised files by adding entries to the `[netcdf_global_attributes]` section of the request file e.g.

```ini
[netcdf_global_attributes]
ensemble = 
```

### I don't need to retrieve data from MASS it's already on disk, how do I use it with CDDS?

CDDS provides a utitily script called `cdds_arrange_input_data` which will `symlink` the files you already have on disk to the appropriate directories.
The typical directory structure CDDS creates looks like this (individual `.pp` and `.nc` files not shown).

```
└── CMIP6
    └── ScenarioMIP
        └── UKESM1-0-LL
            └── ssp126
                └── r1i1p1f2
                    └── cdds_request_ssp126
                        ├── input
                            └── u-dn300
                                ├── ap4
                                ├── ap5
                                └── onm
```

Having made sure you have run the `cdds_create_cdds_directories` first you can then run the arrange script.
Where `/path/to/model/data` is the location on disk containing your model output files.

```bash
cdds_arrange_input_data request.cfg /path/to/model/data
```

The directory structure that your data is in should not matter as the mapping from file to stream is performed using regular expressions.
For example, the contents of `/path/to/model/data` could contain a flat hierarchy with all model files together in one directory.

```
dn300a.p52015apr.pp
dn300a.p42015apr.pp
medusa_dn300o_1m_20150101-20150201_diad-T.nc
```

After running `cdds_arrange_input_data` it would `symlink` the files like so.

```
└── CMIP6
    └── ScenarioMIP
        └── UKESM1-0-LL
            └── ssp126
                └── r1i1p1f2
                    └── cdds_request_ssp126
                        ├── input
                            └── u-dn300
                                ├── ap4
                                    └── dn300a.p42015apr.pp
                                ├── ap5
                                    └── dn300a.p42015apr.pp
                                └── onm
                                    └── medusa_dn300o_1m_20150101-20150201_diad-T.nc
```

!!! note

    The `cdds_arrange_input_data` will `symlink` *all* files that match the filepatterns.
    It will not exclude files outside of the `start` and `end` dates defined in your request, nor will it exclude streams that are not listed in the request.
