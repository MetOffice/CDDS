# Generating CMORised data with CDDS for CMIP6 / CMIP6 Plus simulations using the CDDS Suite

See also [guidance for adhoc generation of CMORised data](../gcmodeldev).

!!! tip
    Use `<script> -h` or `<script> --help` to print information about the script, including available parameters.

!!! example
    A simulation for the pre-industrial control from UKESM will be used as an example in these instructions.

## Prerequisites

Before running the CDDS Operational Procedure, please ensure that:

- [x] you own a *CDDS operational simulation ticket* (see the [list of CDDS operational simulation tickets](https://code.metoffice.gov.uk/trac/cdds/wiki/CMIP6Simulations)) 
      that will monitor the processing of a CMIP6 / CMIP6 Plus simulation using CDDS.

- [x] you belong to the `cdds` group

    !!! tip 
        type `groups` on the command line to print the groups a user is in

- [x] you have write permissions to `moose:/adhoc/projects/cdds/` on MASS

    !!! tip
        You can check if you have correct permissions by running following command and check if your moose username is included 
        in the access control list output:
        ```bash
        moo getacl moose:/adhoc/projects/cdds
        ```

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

### Partial processing of a simulation

In certain circumstances it may be desirable to process and submit a subset of an entire simulation, i.e. the first 250 
years of the `esm-piControl` simulation. Please contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) to discuss this 
prior to starting processing to 

1. Get appropriate guidance on the steps needed to correctly construct the requested variables file in CDDS Prepare
2. Arrange for an appropriate [Errata](https://errata.es-doc.org/static/index.html) to be issued following submission of data sets.

### What to do when things go wrong

On occasion issues will arise with tasks performed by users of CDDS and these will trigger `CRITICAL` error messages in 
the logs and usually require user intervention. Many simple issues (MASS/MOOSE or file system problems) can be resolved 
by re-triggering tasks. When you take any action please ensure that you update your *CDDS operational simulation ticket* 
and if support is needed contact the [CDDS Team](mailto:cdds@metoffice.gov.uk).

## Set up the CDDS operational simulation ticket

- [x] Select `start work` on the *CDDS operational simulation ticket* (so that the status is `in_progress`) to 
      indicate that work is starting. 

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

    2. **Ticket**: Record the version of CDDS being used on the *CDDS operational simulation ticket*.

=== "JASMIN"

    1. Setup the environment to use the central installation of CDDS and its dependencies:
       ```bash
       source ~cdds/bin/setup_env_for_cdds <cdds_version>
       ```
       where `<cdds_version>` is the version of CDDS you wish to use, e.g. `3.3.0`. Unless instructed otherwise 
       you should use the most recent version of CDDS available (to ensure that all bugfixes are picked up), and 
       this version should be used in all stages of the package being processed. If in doubt contact the CDDS team 
       for advice.

    2. **Ticket**: Record the version of CDDS being used on the *CDDS operational simulation ticket*.

!!! note
    * The available version numbers for this script can be found [here](https://github.com/MetOffice/CDDS/tags)
    * If you wish to deactivate the CDDS environment then you can use the command `conda deactivate`.

## Create the request configuration file

The request configuration file is constructed from information in the `rose-suite.info` files within each suite. 

!!! important
    If the `rose-suite.info` file contains incorrect information, this will be propagated through CDDS. As such it is 
    critically important that the information in these files is correct

To construct the request configuration file take the following steps

1. Set up a working directory
    ```bash
    mkdir cdds-example-1
    cd cdds-example-1
    export WORKING_DIR=`pwd`
    ```
    Add the location of your working directory to the *CDDS operational simulation ticket*.

2. Collect required information on the rose suite for the simulation;
    * suite id, e.g. `u-aw310`
    * branch, e.g. `cdds`
    * revision

    !!! info
        You can find the latest revision of the suite branch by using following command:
        ```bash 
        rosie lookup --prefix=u --query project eq u-cmip6 and idx eq <suite id> and branch eq <branch>
        ```

3. Create the request configuration file;
    ```bash
    write_request <suite id> <branch> <revision> <package name> [<list of streams>] -c <pah to proc dir> -t <path to data dir>
    ```

    ??? example
        Create a request configuration file for the rose suite `u-aw310`, branch `cdds` and package `round-20`:
        ```bash
        write_request u-aw310 cdds 115492 round-20 ap4 ap5 ap6 onm inm -c cdds-example-1/proc -t cdds-example-1/data
        ```
        where `cdds-example-1/proc` is the path to the CDDS proc directory and `cdds-example-1/data` the path to the CDDS 
        data directory.

!!! note
    Be careful when re-running CDDS using the same request configuration file: pre-existing data will cause problems for 
    the extraction tasks and pre-existing logs in the proc directory may cause issues when diagnosing problems. If in 
    doubt use a different package name in the request configuration file.

!!! tip
    If necessary the start and end dates for processing can be overridden using the `--start_date` and `--end_date` 
    arguments. Please consult with the [CDDS Team](mailto:cdds@metoffice.gov.uk) if you believe this is necessary.

!!! info
    The log file and request configuration file are written to the current working directory

## Prepare a list of variables to process

!!! warning
    This method does not refer to the data request or CDDS inventory database (to check which datasets have been previously produced), 
    so care should be taken with the choice of variables.

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

!!! note
    If you are using a suite with the CMIP6 STASH set up then you can add the default stream to a list of variables using the command
    ```
    stream_mappings --varfile <filename without streams> --outfile <new file with streams>
    ```
    If you are not using a suite with the CMIP6 STASH configuration then contact us for advice as this process will need to be performed by hand.

## Configure request configuration
!!! important
    The `request.cfg` file contains all information that is needed to process the data through CDDS. The creation of the 
    file does not set all values. So, it must be adjusted manually.

You need to adjust your `request.cfg`:

1. Open the `request.cfg` via a text editor, e.g. `vi` or `gedit`

2. Following values need to be set manually:

| Value                 | Description                                                                       |
|:----------------------|:----------------------------------------------------------------------------------|
| `variable_list_file`  | Path to your variables file                                                       |
| `output_mass_root`    | Path to the moose loction where the data should be archived starts with `moose:`  |
| `output_mass_suffix`  | Sub-directory in MASS to used when moving data.                                   |


!!! note
    Please check the other values as well and do adjustments as needed. For any help, please contact the [CDDS Team](mailto:cdds@metoffice.gov.uk).

!!! info
    The MIP era (`CMIP6` or `CIMP6 Plus`) you are using is defined in the value `mip_era` of the `metdata` section.

## Checkout and configure the CDDS suite

1. Run the following command after replacing values within `<>`:
   ```bash
   checkout_processing_workflow <name for processing suite> \
   <path to request configuration> \
   --workflow_destination .
   ```

    ??? example
        Checkout the CDDS processing suite with the name `my-cdds-test` and the request file location `/home/foo/cdds-example-1/request.cfg`:
        ```
        checkout_processing_workflow my-cdds-test \
        /home/foo/cdds-example-1/request.cfg \
        --workflow_destination .
        ```

    !!! info
        A directory containing a rose workflow will be placed in a subdirectory under the location specified in `--suite_destination`.  
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
   
    ??? example
        Assume:

        * Path to the root proc directory is `/home/foo/cdds-example-1/proc`.
        * Path to the root data directory is `/home/foo/cdds-example-1/data`.
        * MIP era is `CMIP6` and MIP `CMIP`.
        * Model ID is `UKESM1-0-LL` for experiment `piControl` with variant label `r1i1p1f2` and package `round-1`

        Then the command to set the environmental variables is:
        ```bash
        export CDDS_PROC_DIR=/home/foo/cdds-example-1/data/CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1/
        export CDDS_DATA_DIR=/home/foo/cdds-example-1/data/CMIP6/CMIP/UKESM1-0-LL/piControl/r1i1p1f2/round-1/
        ```

3. Run the suite:
   ```bash
   cd <name for processing suite>
   cylc vip .
   ```
   
    ??? example
        If the name of the processing suite is `my-cdds-test`, then run:
        ```bash
        cd my-cdds-test
        cylc vip .
        ```

!!! info
    Cylc 8 is used for running the processing suite. You can do this by running following command before 
    running the suite:
    ```bash
    export CYLC_VERSION=8
    ```

## Monitor conversion suites

For each stream a CDDS Convert suite will be triggered by the processing suite. Each of the suites launched by CDDS Convert 
requires monitoring. This can be done using the command line tool `cylc gui` to obtain a window with an updating summary 
of suites progress or equivalently the [Cylc Review](http://fcm1/cylc-review/) online tools.

Conversion suites will usually be named `cdds_<model id>_<experiment id>_<variant_label>_<stream>` and each stream will 
run completely independently.
If a suite has issues, due to task failure, it will stall, and you will receive an e-mail.

If you hit issues or are unsure how to proceed update the *CDDS operational simulation ticket* for your package with 
anything you believe is relevant (include the location of your working directory) and contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) 
for advice.

The conversion suites run the following steps

- [x] `run_extract_<stream>`

    ??? info "Extract"
        * Run CDDS Extract for this stream. 
        * Runs in `long` queue with a wall time of 2 days.
        * If there are any issues with extracting data they will be reported in the `job.err` log file in the suite and the 
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
        * If in doubt update your *CDDS operational simulation ticket* and contact [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.

- [x] `validate_extract_<stream>`

    ??? info "Extract Validation"
        Validation of the output is now performed as a separate task from extracting it. This task will report missing 
        or unexpected files and unreadable netcdf files.

- [x] `setup_output_dir_<stream>`

    ??? info "Setup Output Directory"
        This task will create output directories for conversion output.

- [x] `mip_convert_<stream>_<grid group>`

    ??? info "MIP Convert"
        * Run MIP Convert to produce output files for a small time window for this simulation.
        * Will retry up to 3 times before suite stalls.
        * CRITICAL issues are appended to `$CDDS_PROC_DIR/convert/log/critical_issues.log`. 
          These will likely need user action to correct for. So, update your *CDDS operational simulation ticket* and 
          contact [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.
        * The CRITICAL log file will not exist if there are no critical issues.
        * A variant named `mip_convert_first_<stream>_<grid group>` may be launched to align the cycling dates with 
          the concatenation processing.

- [x] `finaliser_<stream>`

    ??? info "MIP Convert Finaliser"
        This ensures that concatenation tasks are launched once all MIP Convert tasks have been successfully performed 
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
        * Runs in `long` queue with a wall time of 2 days and can retry up to 3 times before suite stalls 
          (failures are usually due to running out of time while performing a concatenation).
        * Only one `mip_concatenate_batch_<stream>` task can run at one time.
        * Issues can be identified using:
          ```bash
          grep CRITICAL $CDDS_PROC_DIR/convert/log/mip_concatenate_*.log
          ```
          If any critical issues arise or tasks fail update your *CDDS operational simulation ticket* and 
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
        * The approved variables file will have one line per successfully produced dataset of the form: 
          ```bash
          <MIP table>/<variable name>;<Directory containing files>
          ```
        * This task will fail if any QC issues are found and will not resubmit. If this occurs please update your *CDDS operational simulation ticket* 
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
          * An attempt is made to archive data that already exists in MASS. If this occurs please update your *CDDS operational simulation ticket* 
            and contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.

    !!! important "VERY IMPORTANT"
        **Do not delete data from MASS without consultation with [Matt Mizielinski](mailto:matthew.mizielinski@metoffice.gov.uk).**

- [x] `completion_<stream>`

    ??? info "Completion"
        This is a dummy task that is the last thing to run in the suite -- this is to allow inter suite dependencies by 
        allowing the `CDDS workflow` to monitor whether each per stream workflow has completed.

If all goes well the suite will complete, and you will receive an email confirming that the suite has shutdown containing content of the form:
```
Message: AUTOMATIC
See: http://fcm1/cylc-review/taskjobs/<user id>/<suite name>
```

## Prepare *CDDS operational simulation ticket* for review & submission

Once all suites for a particular package have completed update your *CDDS operational simulation ticket* confirming that 
the Extract, Convert, QC and Transfer tasks have been completed.

!!! note
    You can check if suites has completed by using the command `cylc gscan` or using the cylc review tool.

- [x] Copy the request JSON file and any logs to `$CDDS_PROC_DIR`
      ```bash
      cp request.json *.log $CDDS_PROC_DIR/
      ```

- [x] Add a comment to the *CDDS operational simulation ticket* specifying the archived data is ready for submission, 
      and include the full path to your request configuration location.

- [x] Select `assign for review to` on the *CDDS operational simulation ticket* (so that the status is `reviewing`) and 
      assign the *CDDS operational simulation ticket* to Matthew Mizielinski by selecting this name from the list.

- [x] The ticket will then be reviewed according to the [CDDS simulation review procedure](../sim_review) by members of the CDDS team.

!!! info
    The review script used by the CDDS team involves running the following command
    ```bash
    cdds_sim_review <path to the request configuration>
    ```
    checking any CRITICAL issues and following up any other anomalies.


## Run CDDS Teardown

1. Once the approved ticket has been returned to you following submission, delete the contents of the data directory:
    ```bash
    cd <path to the data directory>
    rm -rf input output
    ```
2. Delete all suites used:
    ```bash
    cylc clean cdds_<model_id>_<experiment_id>_<variant_label>_<stream>
    ```
    for each `<stream>` processed, or 
    ```bash
    ls -d ~/cylc-run/cdds_<model_id>_<experiment_id>_<variant_label>_* | xargs cylc clean -y
    ```
    which should find and clear all suites associated with the model, experiment and variant label specified.

3. Update and close the *CDDS operational simulation ticket*
  

