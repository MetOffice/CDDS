The `cdds.convert` subpackage provides the functionality for the `cdds_convert` command (mostly in a further subpackage `cdds.convert.configure_workflow`) as well as supporting code for a number of commands that can only be used in the context of the Cylc conversion workflow.

## cdds_convert

Roughly, the main operations performed by the `cdds_convert` command are  the following

1. Running `generate_user_config_files` (unless explicitly skipped in the `request.cfg`).
1. Determining Jinja2 variable values for use in the Cylc conversion workflow.
1. Copying the Cylc conversion workflow from `cdds.workflows.conversion` [^1] into the users `proc` directory (found under `conversion`).
1. Interpolating the Jina2 variables into the users copy of the processing workflow.
1. Running a specific invocation of `cylc vip` on the processing workflow.

Most of the functionality contained in the modules of `cdds.convert.configure_workflow` is reasonably straightforward.
The one exception being `CalculateISODatetimes`, which is used to determine various durations, cycle frequencies, and dates.


## run_mip_convert

The main purpose of `run_mip_convert` is to

- Interpolate values into the MIP Convert template configuration files created by `generate_user_config_files` for a given cycle point.
- Copy the necessary input files to temporary storage on the node.
- Run the `mip_convert` command in a subprocess.


## mip_batch_concatenate, mip_concatenate, mip_concatenate_organise, mip_concatenate_setup



[^1]:
    Historically the conversion workflow was developed in a separate roses repository (​u-ak283).
    This provided flexibility for modifying the workflow independently (i.e., not needing to re-release CDDS to fix a workflow bug) but did incur greater complexity during development and for initial releases.
