# Generating CMORised data with CDDS for GCModelDev simulations using the CDDS Workflow 

See also [guidance for CMIP6 / CMIP6 Plus generation of CMORised data](cmip6.md).

!!! tip
    Use `<script> -h` or `<script> --help` to print information about the script, including available parameters.

!!! example
    A simulation for the pre-industrial control from HadGEM3 will be used as an example in these instructions.
  
!!! note
    The procedure below assumes that you are keeping track of progress using a *CDDS progress ticket*.
    For exercises such as CMIP6 this was managed centrally, but as GCModelDev is intended to provide support 
    for ad-hoc processing we recommend you have some form of progress note, you are welcome to use 
    [the CDDS Trac](https://code.metoffice.gov.uk/trac/cdds) for this purpose if you wish.

## Prerequisites

Before running the CDDS Operational Procedure, please ensure that:

- [x] you have a project framework to work within (see next section)

- [x] you use a bash shell. CDDS uses Conda which can experience problems running in a shell other than bash.

    !!! tip 
        You can check which shell you use by following command:
        ```bash
        echo $SHELL
        ```
        If the result is not `/bin/bash`, you can switch to a bash shell by running:
        ```bash
        /bin/bash
        ```

If any of the above are not true please contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) for guidance.

### What to do when things go wrong

On occasion issues will arise with tasks performed by users of CDDS and these will trigger `CRITICAL` error messages in 
the logs and usually require user intervention. Many simple issues (MASS/MOOSE or file system problems) can be resolved 
by re-triggering tasks. Support is available via the [CDDS Team](mailto:cdds@metoffice.gov.uk).

## The project framework
The tools we have were written primarily for CMIP6 to CMORise HadGEM3 and UKESM1 model output, but can be applied to other 
projects provided an appropriate set of variable and metadata definitions are available. Defining a new project, e.g. 
CMIP6, requires a reasonable amount of information as does adding an entirely new model configuration and the CDDS team 
should be involved in discussions to do this if you need it. However, it is straightforward to use an existing project 
and include new activities and experiments.

When run in `relaxed` mode CDDS will allow you to use any value for the `mip` (activity id) and `experiment_id`. We have 
a general purpose project for users interested in CMORising data for adhoc use called [GCModelDev](https://github.com/MetOffice/gcmodeldev-cmor-tables) 
which takes the CMIP6 variable definitions and standards, to which we can add new variables as required. This is not 
intended for preparing data for immediate publication to locations such as ESGF, but can be used for analysis alongside 
CMIP6 data and for feeding in to tools that base themselves on the same data structure/standards.

## Activate the CDDS install

=== "MOHC"

    1. Setup the environment to use the central installation of CDDS and its dependencies:
       ```bash
       source ~cdds/bin/setup_env_for_cdds <cdds_version>
       ```
       where `<cdds_version>` is the version of CDDS you wish to use, e.g. `3.0.0`. Unless instructed otherwise 
       you should use the most recent version of CDDS available (to ensure that all bugfixes are picked up), and 
       this version should be used in all stages of the package being processed. If in doubt contact the CDDS team 
       for advice.

    2. **Ticket**: Record the version of CDDS being used on the *CDDS progress ticket*.

=== "JASMIN"

    1. Setup the environment to use the central installation of CDDS and its dependencies:
       ```bash
       source ~cdds/bin/setup_env_for_cdds <cdds_version>
       ```
       where `<cdds_version>` is the version of CDDS you wish to use, e.g. `3.0.0`. Unless instructed otherwise 
       you should use the most recent version of CDDS available (to ensure that all bugfixes are picked up), and 
       this version should be used in all stages of the package being processed. If in doubt contact the CDDS team 
       for advice.

    2. **Ticket**: Record the version of CDDS being used on the *CDDS progress ticket*.

!!! note
    * The available version numbers for this script can be found [here](https://github.com/MetOffice/CDDS/tags) 
      (MetOffice github access required)
    * If you wish to deactivate the CDDS environment then you can use the command `conda deactivate`.

## Create the request configuration file

!!! info
    Please, also the documentation of the [request configuration](../tutorials/request/config_request.md).

A request configuration file contains a number of fields that guide what CDDS processing does and can be viewed as a "control" 
file with a reasonable number of arguments. The simplest approach is to copy an existing file and edit certain fields.

Examples:

* [GCModelDev HadGEM3-GC31-LL](gcmodeldev_examples/HadGEM3-GC31-LL.md)
* [GCModelDev HadGEM3-GC31-LL using ens class](gcmodeldev_examples/HadGEM3-GC31-LL_envs.md)
* [GCModelDev HadGEM3-GC31-MM](gcmodeldev_examples/HadGEM3-GC31-MM.md)
* [GCModelDev UKESM1-0-LL](gcmodeldev_examples/UKESM1-0-LL.md)

These request files should be suitable for use both within the Met Office and on JASMIN.

If you are working with a particular model then to set up a new CDDS processing "package", the user would need to alter 
the experiment_id and/or variant_label fields, possibly the mip, and the workflow_id along with a set of streams

!!! important
    * Check that the `mode` in the `common` section of the request configuration file is set to `relaxed`. In `relaxed` 
      mode CDDS will allow you to use any value for the `mip` (activity id) and `experiment_id`.
    * Check that the `mip_era` in the `metadata` section of the request configuration file is set to `GCModelDev`.

You also need to set following values manually:

| Value                | Description                                                                       |
|:---------------------|:----------------------------------------------------------------------------------|
| `root_proc_dir`      | Path to the CDDS proc directory                                                   |
| `root_data_dir`      | Path to the CDDS data directory                                                   |
| `output_mass_root`   | Path to the moose location where the data should be archived starts with `moose:` |
| `output_mass_suffix` | Sub-directory in MASS to used when moving data.                                   |


!!! info
    The CDDS data directory is the directory where the model output files are written to. The CDDS proc directory is the 
    directory where all the non-data outputs are written to, like the log files.

!!! note
    Please check the other values, as well and do adjustments as needed. For any help, please contact the [CDDS Team](mailto:cdds@metoffice.gov.uk).

## Prepare a list of variables to process

1. Create a text file with the list of variables or copy and modify an existing list. Each line in the file should have the form
   ```bash
   <mip table>/<variable name>:<stream>
   ```

    ??? example
        For example process the variable `tas` for the MIP table `Amon` when processing the `ap5` stream:
        ```bash
        Amon/tas:ap5
        ```

2. Set the value `variable_list_file` in the request configuration to the path of the created variable file.

## Checkout and configure the CDDS workflow

1. Run the following command after replacing values within `<>`:
   ```bash
   checkout_processing_workflow <name for processing workflow> \
   <path to request configuration> \
   --workflow_destination .
   ```

    ??? example
        Checkout the CDDS processing workflow with the name `my-cdds-test` and the request file location `/home/foo/cdds-example-1/request.cfg`:
        ```
        checkout_processing_workflow my-cdds-test \
        /home/foo/cdds-example-1/request.cfg \
        --workflow_destination .
        ```

    !!! info
        A directory containing a rose workflow will be placed in a subdirectory under the location specified in `--workflow_destination`.  
        If this is not specified it will be checked out under `~/roses/`

2. **This step is optional:** Set some useful environmental variables to access the CDDS directories:
   ```bash
   export CDDS_PROC_DIR=/<root_proc_dir>/<mip_era>/<mip>/<model_id>_<experiment_id>_<variant_label>/<package>/
   export CDDS_DATA_DIR=/<root_data_dir>/<mip_era>/<mip>/<model_id>/<experiment_id>/<variant_label>/<package>/
   ls $CDDS_PROC_DIR
   ls $CDDS_DATA_DIR
   ```
   where you must replace all values within `<>`. The `root_proc_dir` and `root_data_dir` are the values that has been 
   specified in the request configuration.

3. Run the workflow:
   ```bash
   cd <name for processing workflow>
   cylc vip . 
   ```

!!! info
    Cylc 8 is used for running the processing workflow. 
    If your default version of cylc is not cylc 8 (run 
    `cylc --version` to check) you will need to run the 
    following command before running the workflow:
    ```bash
    export CYLC_VERSION=8
    ```

## Monitor conversion workflows

For each stream a CDDS Convert workflow will be triggered by the processing workflow. Each of the workflows launched by CDDS Convert 
requires monitoring. This can be done using the command line tool `cylc gui` to obtain a window with an updating summary 
of workflows progress or equivalently the [Cylc Review](http://fcm1/cylc-review/) online tools.

Conversion workflows will usually be named `cdds_<model id>_<experiment id>_<variant_label>_<stream>` and each stream will 
run completely independently.
If a workflow has issues, due to task failure, it will stall, and you will receive an e-mail.

If you hit issues or are unsure how to proceed update the *CDDS progress ticket* for your package with 
anything you believe is relevant (include the location of your working directory) and contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) 
for advice.

The conversion workflows run the following steps

- [x] `run_extract_<stream>`

    ??? info "Extract"
        * Run CDDS Extract for this stream. 
        * Runs in `long` queue with a wall time of 2 days.
        * If there are any issues with extracting data they will be reported in the `job.err` log file in the workflow and the 
          `$CDDS_PROC_DIR/extract/log/cdds_extract_<stream>_<date stamp>.log` log file and the task will fail.
        * The extraction task will automatically resubmit 4 times if it fails and manual intervention is required to proceed.
        * Most issues are related to either MASS (i.e. moo commands failing), file system anomalies (failure to create files /directories) or running out of time.
        * Identify issues either by searching for "CRITICAL" in the `job.err` logs in Cylc Review or by using 
          ```bash 
          grep CRITICAL $CDDS_PROC_DIR/extract/log/cdds_extract_<stream>_<date stamp>.log
          ```
        * If the issue appears to be due to MASS issues you can re-run the failed CDDS Extract job by re-triggering the 
          `run_extract_<stream>` task via the cylc gui or via the cylc command line tools:
          ```bash
          cylc trigger cdds_<model id>_<experiment id>_<variant label>_<stream> run_extract_<stream>:failed
          ```
        * If in doubt update your *CDDS progress ticket* and contact [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.

- [x] `validate_extract_<stream>`

    ??? info "Extract Validation"
        Validation of the output is now performed as a separate task from extracting it. This task will report missing 
        or unexpected files and unreadable netCDF files.

- [x] `setup_output_dir_<stream>`

    ??? info "Setup Output Directory"
        This task will create output directories for conversion output.

- [x] `mip_convert_<stream>_<grid group>`

    ??? info "MIP Convert"
        * Run MIP Convert to produce output files for a small time window for this simulation.
        * Will retry up to 3 times before workflow stalls.
        * CRITICAL issues are appended to `$CDDS_PROC_DIR/convert/log/critical_issues.log`. 
          These will likely need user action to correct for. So, update your *CDDS progress ticket* and 
          contact [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.
        * The CRITICAL log file will not exist if there are no critical issues.
        * A variant named `mip_convert_first_<stream>_<grid group>` may be launched to align the cycling dates with 
          the concatenation processing.

- [x] `finaliser_<stream>`

    ??? info "MIP Convert Finaliser"
        This ensures that Concatenation Tasks are launched once all MIP Convert tasks have been successfully performed 
        for a particular time range. This step **should** never fail.

- [x] `organise_files_<stream>`

    ??? info "Organise Files"
        * Re-arranges the output files on disk from a directory structure created by the MIP Convert tasks of the form 
        ```bash
        $CDDS_DATA_DIR/output/<stream>_mip_convert/<YYYY-MM-DD>/<grid>/<files>
        ```
        to 
        ```bash
        $CDDS_DATA_DIR/output/<stream>_concat/<MIP table>/<variable name>/<files>
        ```
        * Ready for concatenation. A variation named `organise_files_final_<stream>` does the same thing but at the end 
          of the conversion process.
 
- [x] `mip_concatenate_setup_<stream>`

    ??? info "MIP Concatenate Setup"
        * This step constructs a list of concatenation jobs that must be performed

- [x] `mip_concatenate_batch_<stream>`

    ??? info "MIP Concatenate Batch"
        * Perform the concatenation commands (`ncrcat`) required to join small files together. 
        * Runs in `long` queue with a wall time of 2 days and can retry up to 3 times before workflow stalls 
          (failures are usually due to running out of time while performing a concatenation).
        * Only one `mip_concatenate_batch_<stream>` task can run at one time.
        * Issues can be identified using:
          ```bash
          grep CRITICAL $CDDS_PROC_DIR/convert/log/mip_concatenate_*.log
          ```
          If any critical issues arise or tasks fail update your *CDDS progress ticket* and 
          contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.
        * Output data is written to 
          ```bash
          $CDDS_DATA_DIR/output/<stream>/<MIP table>/<variable name>/<files>
          ```

- [x] `run_qc_<stream>`

    ??? info "Quality Check (QC)"
        * Run the QC process on output data for this stream
        * Produces a report at:
          ```bash
          $CDDS_PROC_DIR/qualitycheck/report_<stream>_<datestamp>.json
          ```
          and a list of variables which pass the quality checks at:
          ```bash
          $CDDS_PROC_DIR/qualitycheck/approved_variables_<stream>_<datestamp>.txt
          ```
          and a log file at:
          ```bash
          $CDDS_PROC_DIR/qualitycheck/log/qc_run_and_report_<stream>_<datestamp>.log
          ```
        * The approved variables file will have one line per successfully produced Dataset of the form: 
          ```bash
          <MIP table>/<variable name>;<Directory containing files>
          ```
        * This task will fail if any QC issues are found and will not resubmit. If this occurs please update your *CDDS progress ticket* 
          and contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice. 
 
- [x] `run_transfer_<stream>`

    ??? info "Transfer"
        * Archive data for variables that are marked active in the requested variables file produced by CDDS Prepare and 
          have successfully passed the QC checks, i.e. are listed in the approved variables file.
        * Will not automatically retry, even if failure was due to MASS/MOOSE issues.
        * The location in MASS to which these data are archived is determined by the `output_mass_suffix` argument 
          specified in the request configuration file.
        * Task will fail if
          * There are MASS issues: For example if the following command returns anything there has been a MASS outage and you can re-trigger the task:
            ```bash
            grep SSC_STORAGE_SYSTEM_UNAVAILABLE $CDDS_PROC_DIR/archive/log/cdds_store_<stream>_<date stamp>.log
            ```
          * An attempt is made to archive data that already exists in MASS. If this occurs please update your *CDDS progress  ticket* 
            and contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.

    !!! important "VERY IMPORTANT"
        **Do not delete data from MASS without consultation with [Matt Mizielinski](mailto:matthew.mizielinski@metoffice.gov.uk).**

- [x] `completion_<stream>`

    ??? info "Completion"
        This is a dummy task that is the last thing to run in the workflow -- this is to allow inter workflow dependencies by 
        allowing the `CDDS workflow` to monitor whether each per stream workflow has completed.

If all goes well the workflow will complete, and you will receive an email confirming that the workflow has shutdown containing content of the form:
```
Message: AUTOMATIC
See: http://fcm1/cylc-review/taskjobs/<user id>/<workflow name>
```
