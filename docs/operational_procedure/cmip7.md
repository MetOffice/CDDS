# Generating CMORised data with CDDS for CMIP7 simulations using the CDDS Workflow

!!! tip
    Use `<script> -h` or `<script> --help` to print information about the script, including available parameters.

## Prerequisites

Before running the CDDS Operational Procedure, please ensure that:

- [x] You own a *CDDS operational simulation ticket* (see the [list of CDDS operational simulation tickets](https://github.com/UKNCSP/CDDS-CMIP7-processing/issues)) that will monitor the processing of a CMIP7 simulation using CDDS. It is important that this is maintained throughout processing to clearly document the process.

- [x] You belong to the `cdds` group.

    !!! tip 
        Type `groups` on the command line to print the groups a user is in.

- [x] You have write permissions to `moose:/adhoc/projects/cdds/` on MASS.

    !!! tip
        You can check if you have correct permissions by running following command and check if your moose username is included 
        in the access control list output:
        ```bash
        moo getacl moose:/adhoc/projects/cdds
        ```

- [x] You use a bash shell. CDDS uses Conda which can experience problems running in a shell other than bash.

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

### Packages

CDDS is designed to handle a "package" of simulation data at one time; a set of variables from a particular simulation 
run. Multiple "packages" can be run for a given simulation to add new or corrected variables to the archive. Each package 
should be run using a separate processing (`proc`) and `data` directory. The simplest way to separate two run throughs 
of CDDS is to use a different package name. This is set either when running the `write_request` script below or by modifying 
the request configuration itself.

### Partial processing of a simulation

In certain circumstances it may be desirable to process and submit a subset of an entire simulation, i.e. the first 250 
years of the `esm-piControl` simulation. Please contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) to discuss this 
prior to starting processing to:

1. Get appropriate guidance on the steps needed to correctly construct the requested variables file in CDDS Prepare.
2. Arrange for an appropriate [Errata](https://errata.es-doc.org/static/index.html) to be issued following submission of data sets.

### What to do when things go wrong

On occasion issues will arise with tasks performed by users of CDDS and these will trigger `CRITICAL` error messages in 
the logs and usually require user intervention. Many simple issues (MASS/MOOSE or file system problems) can be resolved 
by re-triggering tasks. When you take any action please ensure that you update your *CDDS operational simulation ticket* 
and if support is needed contact the [CDDS Team](mailto:cdds@metoffice.gov.uk).

## Set up the CDDS operational simulation ticket

- [x] On the *CDDS operational simulation ticket* add the label `in_progress` to indicate that work is starting. 

## Activate the CDDS install

=== "MOHC"

    1. Setup the environment to use the central installation of CDDS and its dependencies:
       ```bash
       source ~cdds/bin/setup_env_for_cdds <cdds_version>
       ```
       where `<cdds_version>` is the version of CDDS you wish to use, e.g. `3.3.3`. Unless instructed otherwise 
       you should use the most recent version of CDDS available (to ensure that all bugfixes are picked up), and 
       this version should be used in all stages of the package being processed. If in doubt contact the CDDS team 
       for advice.

    2. **Ticket**: Record the version of CDDS being used on the *CDDS operational simulation ticket*.

=== "JASMIN"

    1. Setup the environment to use the central installation of CDDS and its dependencies:
       ```bash
       source ~cdds/bin/setup_env_for_cdds <cdds_version>
       ```
       where `<cdds_version>` is the version of CDDS you wish to use, e.g. `3.3.3`. Unless instructed otherwise 
       you should use the most recent version of CDDS available (to ensure that all bugfixes are picked up), and 
       this version should be used in all stages of the package being processed. If in doubt contact the CDDS team 
       for advice.

    2. **Ticket**: Record the version of CDDS being used on the *CDDS operational simulation ticket*.

!!! note
    * The available version numbers for this script can be found [here](https://github.com/MetOffice/CDDS/tags).
    * If you wish to deactivate the CDDS environment then you can use the command `conda deactivate`.

## Create the request configuration file and variable list

The request configuration file is constructed from information submitted for each workflow in the workflow_metadata directory of the [CDDS-simulation-metadata](https://github.com/UKNCSP/CDDS-simulation-metadata/tree/main/workflow_metadata) repository. 

!!! important
    If the workflow metadata configuration file contains incorrect information, this will be propagated through CDDS. As such, it is 
    critically important that the information in these files is correct.

To construct the request configuration file take the following steps

1. Set up a working directory
    ```bash
    mkdir cdds-example-1
    cd cdds-example-1
    export WORKING_DIR=`pwd`
    ```
    Add the location of your working directory to the *CDDS operational simulation ticket*.

2. Navigate to the issues section of the [CDDS-simulation-metadata](https://github.com/UKNCSP/CDDS-simulation-metadata/issues) repository and create a new  issue using the template titled *Request the Generation Of A CDDS Request File*. You will need to provide the model workflow ID (sometimes known as suite ID) that you wish to generate a request file for, the streams you wish to process with and a package name (see the packages information given above).
   **Ticket**: Add a note of the issue number for this request file generation to the *CDDS operational simulation ticket*.

If you experience any issues that you cannot resolve please contact the [CDDS Team](mailto:cdds@metoffice.gov.uk).

3. Download a copy of the generated request file and its associated variable list, save them to your working directory and attach a copy to the *CDDS operational simulation ticket*. The associated variable list can be found in the `variables/` directory of the [CDDS-simulation-metadata](https://github.com/UKNCSP/CDDS-simulation-metadata/issues) repository. All variable list files are named in the format of `<model_workflow_id>_<experiment>_<model>.txt` (e.g. if you are running u-dv341 using the experiment piControl and the model UKCM2-0-LL, the variable list file will be named `u-dv341_piControl_UKCM2-0-LL.txt`).

    !!! important
        Do not attempt to edit the request file directly on the [CDDS-simulation-metadata](https://github.com/UKNCSP/CDDS-simulation-metadata) repository. Changes should only be made to your locally downloaded copy. Any changes should be documented in the *CDDS operational simulation ticket*.
    !!! important
        You may find that the `variables/` directory contains multiple version subdirectories. Please use the most recent version available to you at that time. These version directories are associated with the version of the data request used to produce the variable list. **Ticket**: Add a note of the version directory that the variable list was obtained from to the *CDDS operational simulation ticket*.

!!! note
    Be careful when re-running CDDS using the same request configuration file: pre-existing data will cause problems for 
    the extraction tasks and pre-existing logs in the proc directory may cause issues when diagnosing problems. If in 
    doubt use a different package name in the request configuration file.

!!! tip
    If necessary ammendments to parameters such as start and end dates for processing can be changed in the request file. Please consult with the [CDDS Team](mailto:cdds@metoffice.gov.uk) if you believe this is necessary and document the change in the *CDDS operational simulation ticket*.

## Configure request configuration
!!! important
    The `request.cfg` file contains all information that is needed to process the data through CDDS. The creation of the 
    file does not set all values. So, it must be adjusted manually.

You need to adjust your `request.cfg`:

1. Open the `request.cfg` via a text editor, e.g. `vi` or `gedit`.

2. The following values need to be set manually:

| Value                 | Description                                                                       |
|:----------------------|:----------------------------------------------------------------------------------|
| `variable_list_file`  | Path to your variable list file                                                       |

!!! note
    Please check the other values as well and do adjustments as needed. Ensure any adjustments are recorded on the *CDDS operational simulation ticket*. For any help, please contact the [CDDS Team](mailto:cdds@metoffice.gov.uk).

!!! info
    The MIP era (`CMIP7`) you are using is defined in the value `mip_era` of the `metadata` section.

## Run the CDDS workflow for a single request

If running a single request configuration, please follow the standard process as described in the [Quickstart tutorial](https://metoffice.github.io/CDDS/latest/tutorials/quickstart/). Assuming you have your request file and variable list set up, this simply involves running the following 4 commands:

1. Activate the environment:
   ```bash
   source ~cdds/bin/setup_env_for_cdds <the version of CDDS you are using, e.g. 3.3.3>
   ```
2. Create the directory structure:
   ```bash
   create_cdds_directory_structure <the path to your request.cfg>
   ```
3. Create the internal variable lists used by CDDS:
   ```bash
   prepare_generate_variable_list <the path to your request.cfg>
   ```
4. Launch the cylc conversion workflow:
   ```bash
   cdds_convert <the path to your request.cfg>
   ```

This process can be monitored via the cylc gui or cylc review. If a workflow has issues, due to task failure, it will stall, and you will receive an e-mail.Further guidence on this process can be found in the [Quickstart tutorial](https://metoffice.github.io/CDDS/latest/tutorials/quickstart/). 

## Checkout and configure the CDDS workflow for a batch of requests

Alternatively, if you will be running a large batch of request files, it may be more valuable to use the processing workflow tool.

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
   export CDDS_DATA_DIR=/<root_data_dir>/<mip_era>/<mip>/<model_id>_<experiment_id>_<variant_label>/<package>/
   ls $CDDS_PROC_DIR
   ls $CDDS_DATA_DIR
   ```
   where you must replace all values within `<>`. The `root_proc_dir` and `root_data_dir` are the values that has been 
   specified in the request configuration.
   
    ??? example
        Assume:

        * Path to the root proc directory is `/home/foo/cdds-example-1/proc`.
        * Path to the root data directory is `/home/foo/cdds-example-1/data`.
        * MIP era is `CMIP7` and MIP `CMIP`.
        * Model ID is `UKESM1-0-LL` for experiment `piControl` with variant label `r1i1p1f2` and package `round-1`

        Then the command to set the environmental variables is:
        ```bash
        export CDDS_PROC_DIR=/home/foo/cdds-example-1/data/CMIP7/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1/
        export CDDS_DATA_DIR=/home/foo/cdds-example-1/data/CMIP7/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1/
        ```

3. Run the workflow:
   ```bash
   cd <name for processing workflow>
   cylc vip .
   ```
   
    ??? example
        If the name of the processing workflow is `my-cdds-test`, then run:
        ```bash
        cd my-cdds-test
        cylc vip .
        ```

!!! info
    Cylc 8 is used for running the processing workflow. You can do this by running following command before 
    running the workflow:
    ```bash
    export CYLC_VERSION=8
    ```

### Monitor conversion workflows

For each stream, a CDDS Convert workflow will be triggered by the processing workflow. Each of the workflows launched by CDDS Convert 
requires monitoring. This can be done using the command line tool `cylc gui` to obtain a window with an updating summary 
of workflows progress or equivalently the [Cylc Review](http://fcm1/cylc-review/) online tools.

Conversion workflows will usually be named `cdds_<workflow_base_name>_<stream>` and each stream will 
run completely independently.
If a workflow has issues, due to task failure, it will stall, and you will receive an e-mail.

If you hit issues or are unsure how to proceed update the *CDDS operational simulation ticket* for your package with 
anything you believe is relevant (include the location of your working directory) and contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) 
for advice.

The conversion workflows run the following steps:

- [x] `run_extract_<stream>`

    ??? info "Extract"
        * Run CDDS Extract for this stream. 
        * Runs in `long` queue with a wall time of 2 days.
        * If there are any issues with extracting data they will be reported in the `job.out` log file in the workflow and the 
          `$CDDS_PROC_DIR/extract/log/cdds_extract_<stream>_<date stamp>.log` log file and the task will fail.
        * The extraction task will automatically resubmit 4 times if it fails and manual intervention is required to proceed.
        * Most issues are related to either MASS (i.e. moo commands failing), file system anomalies (failure to create files /directories) or running out of time.
        * Identify issues either by searching for "CRITICAL" in the `job.out` logs in Cylc Review or by using 
          ```bash 
          grep CRITICAL $CDDS_PROC_DIR/extract/log/cdds_extract_<stream>_<date stamp>.log
          ```
        * If the issue appears to be due to MASS issues you can re-run the failed CDDS Extract job by re-triggering the 
          `run_extract_<stream>` task via the cylc gui or via the cylc command line tools:
          ```bash
          cylc trigger cdds_<workflow_base_name>_<stream> run_extract_<stream>:failed
          ```
        * If in doubt update your *CDDS operational simulation ticket* and contact [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.

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
          These will likely need user action to correct for. So, update your *CDDS operational simulation ticket* and 
          contact [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.
        * The CRITICAL log file will not exist if there are no critical issues.
        * A variant named `mip_convert_first_<stream>_<grid group>` may be launched to align the cycling dates with 
          the concatenation processing.

- [x] `finaliser_<stream>`

    ??? info "MIP Convert Finaliser"
        This ensures that Concatenation Tasks are launched once all MIP Convert tasks have been successfully performed 
        for a particular time range. This step **should** never fail.

    ??? note
        If this task fails, the reason is that the adjustment of the memory and time limits failed. So, please resubmit the task.

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
        * The approved variables file will have one line per successfully produced Dataset of the form: 
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
        **Do not delete data from MASS without consultation with [CDDS support](mailto:cdds@metoffice.gov.uk).**

- [x] `completion_<stream>`

    ??? info "Completion"
        This is a dummy task that is the last thing to run in the workflow -- this is to allow inter workflow dependencies by 
        allowing the `CDDS workflow` to monitor whether each per stream workflow has completed.

If all goes well the workflow will complete. Please be sure to periodically check on your workflows progress and confirm that it has completed before updating your *CDDS operational simulation ticket*.

## Prepare *CDDS operational simulation ticket* for review & submission

Once all workflows for a particular package have completed update your *CDDS operational simulation ticket* confirming that 
the Extract, Convert, QC and Transfer tasks have been completed.

!!! note
    You can check if workflows has completed by using the command `cylc gscan` or using the cylc review tool.

- [x] Copy the request JSON file and any logs to `$CDDS_PROC_DIR`.
      ```bash
      cp request.json *.log $CDDS_PROC_DIR/
      ```

- [x] Add a comment to the *CDDS operational simulation ticket* specifying the archived data is ready for submission, 
      and include the full path to your request configuration location.

- [x] Add the label `assign for review to` to the *CDDS operational simulation ticket* and 
      assign the *CDDS operational simulation ticket* to Matthew Mizielinski by selecting this name from the list.

- [x] The ticket will then be reviewed according to the [CDDS simulation review procedure](sim_review.md) by members of the CDDS team.

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
2. Delete all workflows used:
    ```bash
    cdds_clean <path to the request configuration>
    ```

3. Update and close the *CDDS operational simulation ticket*.
  

