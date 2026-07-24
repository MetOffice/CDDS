# Generating CMORised data with CDDS for CMIP7 simulations using the CDDS Workflow

!!! tip
    Use `<script> -h` or `<script> --help` to print information about the script, including available parameters.

## 1. Simulation registration

Before processing data for CMIP7 your simulation metadata must be registered via the [CDDS-simulation-metadata](https://github.com/UKNCSP/CDDS-simulation-metadata)
repository. Please create an issue via the [Add/Modify Workflow Metadata](https://github.com/UKNCSP/CDDS-simulation-metadata/issues/new?template=add_workflow_metadata.yml) form. Please be mindful that this is a public repository.

Once **successful**  a workflow metadata file will be created in the [workflow_metadata](https://github.com/UKNCSP/CDDS-simulation-metadata/tree/main/workflow_metadata)
named according to the workflow id, and the table of runs [here](https://ukncsp.github.io/CDDS-simulation-metadata/) will be updated. 
A list of variables requested in the [CMIP7 Data Request](https://wcrp-cmip.org/cmip-phases/cmip7/cmip7-data-request/) will be produced and 
added to the [variables](https://github.com/UKNCSP/CDDS-simulation-metadata/tree/main/variables) directory organised by Data Request version (e.g. v1.2.2.5). 
All variable list files are named in the format of `<model_workflow_id>_<experiment>_<model>.txt` (e.g. if you are running u-dv341 using the experiment piControl and the model UKCM2-0-LL, the variable list file will be named `u-dv341_piControl_UKCM2-0-LL.txt`).
Please use the most recent Data Request version for processing unless you have a *very* good reason that you have discussed with the CDDS team.

Attempts to register workflow metadata that do not match the definition in the [CMIP7 CVs](https://esgvoc.ipsl.fr/?projects=cmip7) will fail. If an experiment has not yet been registered or the parent information is inconsistent with the definition within CMIP7 the github actions will fail and a comment will be added to the issue to this effect.

!!! important
    If the workflow metadata file contains incorrect information, this will be propagated through CDDS. As such, it is 
    critically important that the information in these files is correct. Once data has been published it takes a 
    non-trivial amount of effort to correct the problem, so please check that the data provided here is correct.

## 2. Request file generation

The request file is the core control file used to control CDDS and simulations need to be registered in order to generate one.  
The form [here](https://github.com/UKNCSP/CDDS-simulation-metadata/issues/new?template=generate_request_file.yml) can be used to generate a request; 
enter the workflow id, select the platform (Met Office or JASMIN), select the streams to be processed (see sub section below) and add a package name that is 
unique for the simulation being processed.

Note that certain fields within the request need to be manually updated and paths updated prior to use.

    !!! important
        Do not attempt to edit the request file directly on the [CDDS-simulation-metadata](https://github.com/UKNCSP/CDDS-simulation-metadata) repository. Changes should only be made to your locally downloaded copy. Any changes should be documented in the *CDDS operational simulation issue* (created in the next step).


### Streams

Typical streams used for CDDS;

| stream id | format | frequency | notes |
| --- | --- | --- | ---| 
| afx | PP | fx | Fixed fields such as masks and orography| 
| ap4 | PP | monthly | |
| ap5 | PP | monthly | |
| apu | PP | monthly | Unpacked data |
| ap6 | PP | daily | |
| ap7 | PP | 6 hourly | |
| ap8 | PP | 3 hourly | |
| ap9 | PP | hourly | |
| apt | PP | timestep | usually only used for site specific data |
| ofx | netCDF | fx | Fixed fields such as masks| 
| onm | netCDF | monthly | ocean |
| ond | netCDF | daily | ocean |
| inm | netCDF | monthly | sea-ice |
| ind | netCDF | daily | sea-ice |

Other streams *may* be usable, but please contact the CDDS team for advice.

### Packages

CDDS is designed to handle a "package" of simulation data at one time; a set of variables from a particular simulation 
run. Multiple "packages" can be run for a given simulation to add new or corrected variables to the archive. Each package 
should be run using a separate processing (`proc`) and `data` directory. The simplest way to separate two run throughs 
of CDDS is to use a different package name. This is set through the `package` entry in the `[common]` section of the
request file.

We recommend using either sequential names (*round-1*, *round-2*, etc) or a datestamp (*round-2026-08-01*) for the `package` field.

!!! important
    Please ensure that package names are unique for a particular run through of CDDS. Failing to do this can lead to multiple problems and confusion when debugging problems.

### Partial processing of a simulation

In certain circumstances it may be desirable to process and submit a subset of an entire simulation, i.e. the first 250 
years of the `esm-piControl` simulation. Please contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) to discuss this 
prior to starting processing to:

1. Get appropriate guidance on the steps needed to correctly construct the request and variables file.
2. Arrange for an appropriate [Errata](https://errata.esgf.io) to be issued following submission of data sets.


## 3. Creating an operational simulation issue

The *CDDS operational simulation issue*, see the [list of CDDS operational simulation issues](https://github.com/UKNCSP/CDDS-CMIP7-processing/issues), is the 
primary route for documenting progress of processing and for requesting support with processing.

Once you have a request file (see above) and are ready to start processing please fill out the 
[form to create a new operational issue](https://github.com/UKNCSP/CDDS-CMIP7-processing/issues/new?template=ticket.yml), 
reporting the workflow ID, package and either linking to the request file and variables list or indicating that you would will attach the files directly to the issue.

When you are ready to start work on this issue please add the `in progress` label.

## 4. Prerequisites for running

Before proceeding with the CDDS Operational Procedure, please ensure that:

- [x] You belong to the `cdds-data` group.

    !!! tip 
        Type `groups` on the command line to print the groups a user is in.

- [x] You have write permissions to `moose:/adhoc/projects/cdds/` on MASS.

    !!! tip
        You can check if you have correct permissions by running following command and check if your moose username is included 
        in the access control list output:
        ```bash
        moo getacl moose:/adhoc/projects/cdds
        ```
        If your user id is not included with the `readwrite-delete` permissions listed please contact the CDDS team so that you can be given the required permissions to archive data.

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

## 5. Activate the CDDS install

=== "MOHC"

    1. Setup the environment to use the central installation of CDDS and its dependencies:
       ```bash
       source ~cdds/bin/setup_env_for_cdds <cdds_version>
       ```
       where `<cdds_version>` is the version of CDDS you wish to use, e.g. `4.0.0`. Unless instructed otherwise 
       you should use the most recent version of CDDS available (to ensure that all bugfixes are picked up), and 
       this version should be used in all stages of the package being processed. If in doubt contact the CDDS team 
       for advice.

    2. **Issue**: Record the version of CDDS being used on the *CDDS operational simulation issue*.

=== "JASMIN"

    1. Setup the environment to use the central installation of CDDS and its dependencies:
       ```bash
       source ~cdds/bin/setup_env_for_cdds <cdds_version>
       ```
       where `<cdds_version>` is the version of CDDS you wish to use, e.g. `4.0.0`. Unless instructed otherwise 
       you should use the most recent version of CDDS available (to ensure that all bugfixes are picked up), and 
       this version should be used in all stages of the package being processed. If in doubt contact the CDDS team 
       for advice.

    2. **Issue**: Record the version of CDDS being used on the *CDDS operational simulation issue*.

!!! note
    * The available version numbers for this script can be found [here](https://github.com/MetOffice/CDDS/tags).
    * If you wish to deactivate the CDDS environment then you can use the command `conda deactivate`.

## 6. Create a working directory and modify request config file

We recommend a separate working directory for each CDDS package for clarity. Download the request config file and variables list and make any modifications updating your *CDDS operational simulation issue* accordingly.

!!! important
    The `request.cfg` file contains all information that is needed to process the data through CDDS. The process of creating a request file on github does 
    not set all values, it must be adjusted manually.

You will need to adjust your `request.cfg`:

1. Open the `request.cfg` via a text editor, e.g. `vi` or `gedit`.

2. The following values need to be set manually:

| Value                 | Description                             |
|:----------------------|:----------------------------------------|
| `variable_list_file`  | Full Path to your variable list file    |

!!! note
    Please check the other values as well and make adjustments as needed. Ensure any adjustments are recorded on the *CDDS operational simulation issue*. For any help, please contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) or tag `@UKNCSP/cdds` on your issue.

!!! info
    The MIP era (`CMIP7`) you are using is defined in the value `mip_era` of the `metadata` section.

## 7. Run the CDDS workflow 

If running a single request configuration, please follow the standard process as described in the [Quickstart tutorial](https://metoffice.github.io/CDDS/latest/tutorials/quickstart/). Assuming you have your request file and variable list set up, this simply involves running the following 4 commands:

1. Activate the environment:
   ```bash
   source ~cdds/bin/setup_env_for_cdds <the version of CDDS you are using, e.g. 4.0.0>
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

<!--
## Checkout and configure the CDDS workflow for a batch of requests

Alternatively, if you will be running a large batch of request files, it may be more valuable to use the processing workflow tool.

1. Set up a working directory
    ```bash
    mkdir cdds-example-1
    cd cdds-example-1
    export WORKING_DIR=`pwd`
    ```
    Add the location of your working directory to the *CDDS operational simulation issue*.

2. Run the following command after replacing values within `<>`:
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

3. **This step is optional:** Set some useful environmental variables to access the CDDS directories:
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

4. Run the workflow:
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
-->

### Monitor conversion workflow

A single cylc workflow will be launched by the `cdds_convert` command which requires monitoring by the user to handle an issues encountered. 
This can be done using cylchub, the cylc tui command or the cylc review service.

Conversion workflows will usually be named `cdds_<workflow_base_name>_<stream>` and each stream will 
run completely independently.
If a workflow has issues, due to task failure, it will stall, and you will receive an e-mail.

If you hit issues or are unsure how to proceed update the *CDDS operational simulation issue* for your package with 
anything you believe is relevant (include the location of your working directory) add the label `help needed` and tag `@UKNCSP/cdds` or 
email the [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.

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
        * If in doubt update your *CDDS operational simulation issue* and contact [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.

- [x] `validate_extract_<stream>`

    ??? info "Extract Validation"
        Validation of the output is now performed as a separate task from extracting it. This task will report missing 
        or unexpected files and unreadable netCDF files.

- [x] `setup_output_dir_<stream>`

    ??? info "Setup Output Directory"
        This task will create output directories for conversion output.

- [x] `initialiser_<stream>`
    ??? info "MIP Convert initialiser"
        Used to manage flow of tasks.

- [x] `mip_convert_<stream>_<grid group>`

    ??? info "MIP Convert"
        * Run MIP Convert to produce output files for a small time window for this simulation.
        * Will retry up to 3 times before workflow stalls.
        * CRITICAL issues are appended to `$CDDS_PROC_DIR/convert/log/critical_issues.log`. 
          These will likely need user action to correct for. So, update your *CDDS operational simulation issue* and 
          contact [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.
        * The CRITICAL log file will not exist if there are no critical issues.
        * A variant named `mip_convert_first_<stream>_<grid group>` may be launched to align the cycling dates with 
          the concatenation processing.

- [x] `finaliser_<stream>`

    ??? info "MIP Convert Finaliser"
        This ensures that Concatenation Tasks are launched once all MIP Convert tasks have been successfully performed 
        for a particular time range. It also updates time, memory and disk usage requirements for the processing to 
        optimise use of SLURM queues.

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
          If any critical issues arise or tasks fail update your *CDDS operational simulation issue* and 
          tag `@UKNCSP/cdds` or contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.
        * Output data is written to 
          ```bash
          $CDDS_DATA_DIR/output/<stream>/<MIP table>/<variable name>/<files>
          ```
- [x] `run_repack_<stream>`
    ??? info "Repacking
        Runs the [CMIP7 repacking tools](https://github.com/NCAS-CMS/cmip7_repack) on all output to optimise the data for reading.

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
        * This task will fail if any QC issues are found and will not resubmit. If this occurs please update your *CDDS operational simulation issue* 
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
          * An attempt is made to archive data that already exists in MASS. If this occurs please update your *CDDS operational simulation issue* 
            and tag `@UKNCSP/cdds` add the `help needed` label to your issue  or contact the [CDDS Team](mailto:cdds@metoffice.gov.uk) for advice.

    !!! important "VERY IMPORTANT"
        **Do not attempt to delete data from MASS without consultation with [CDDS support](mailto:cdds@metoffice.gov.uk).**

- [x] `run_sim_review`
    ??? info "Simulation review"
        To ease the submission process our automated review script is run as the last task in the workflow. We will use this to determine whether
        data is fit for publication.

- [x] `workflow_complete`

    ??? info "Completion"
        This is a dummy task that is the last thing to run in the workflow -- this is to support inter workflow dependencies 

If all goes well the workflow will complete. Please be sure to periodically check on your workflows progress and confirm that it has completed before updating your *CDDS operational simulation issue*.

### What to do when things go wrong

On occasion issues will arise with tasks performed by users of CDDS and these will trigger `CRITICAL` error messages in 
the logs and usually require user intervention. Many simple issues (MASS/MOOSE or file system problems) can be resolved 
by re-triggering tasks. When you take any action please ensure that you update your *CDDS operational simulation issue* 
and if support is needed add the `help needed` label and mention `@UKNCSP/cdds` to alert the CDDS team.

## 8. Prepare *CDDS operational simulation issue* for review & submission

Once the workflows for a particular package have completed update your *CDDS operational simulation issue* confirming that 
the Extract, Convert, QC and Transfer tasks have been completed.

- [x] Copy the request JSON file and any logs to `$CDDS_PROC_DIR`.
      ```bash
      cp request.json *.log $CDDS_PROC_DIR/
      ```

- [x] Add a comment to the *CDDS operational simulation issue* specifying the archived data is ready for submission, 
      and include the full path to your request configuration location.

- [x] Add the label `ready for submission` to the *CDDS operational simulation issue* and 
      assign it to Matthew Mizielinski by selecting this name from the list.

- [x] The issue will then be reviewed according to the [CDDS simulation review procedure](sim_review.md) by members of the CDDS team.


## 9. Run CDDS Teardown

1. Once the approved issue has been returned to you following submission, delete the contents of the data directory:
    ```bash
    cd <path to the data directory>
    rm -rf input output
    ```
2. Delete all workflows used:
    ```bash
    cdds_clean <path to the request configuration>
    ```

3. Update and close the *CDDS operational simulation issue*.
  

