# Conversion Section

The `conversion` in the request configuration contains settings that specify how CDDS is run.

## Configuration Values

`skip_extract`
:   skip the extract task at the start of the CDDS suite for each stream.

    **Default**: `False`, on Jasmin `True`

`skip_extract_validation`
:   skip validation at the end of the extract task.

    **Default:** `False`

`skip_configure`
:   skip the configure step of the CDDS suite for each stream.

    **Default:** `False`

`skip_qc`
:   skip the quality control task of the CDDS suite for each stream.

    **Default:** `False`

`skip_archive`
:   skip the archive task at the end of the CDDS suite for each stream.

    **Default:** `False`, on Jasmin `True`

`cdds_workflow_branch`
:   branch of the CDDS suite that should be used.

    **Default:** The value that is stored in the environment variable `CDDS_CONVERT_WORKFLOW_BRANCH`

`cylc_args`
:   arguments to be passed to cylc vip for the CDDS processing suite.

    **Default:** `-v`

`no_email_notifications`
:   no email notifications will be sent from the suites.

    **Default:** `True`

`scale_memory_limits`
:   memory scaling factor to be applied to all batch jobs. Please, contact the [CDDS team](mailto:cdds@metoffice.gov.uk) 
    for advice.

`override_cycling_frequency`
:   override default frequency for specified stream. Each stream should be specified along with the cycling frequency 
    using the format `<stream>=<frequency>`, e.g. `ap7=P3M ap8=P1M`.

`model_params_dir`
:   the path to the directory containing the model parameters that should be overloaded the model parameters in the plugin.

`continue_if_mip_convert_failed`
:   specify if the MIP convert task will fail if any errors occur or only if the data of *all* streams can not be processed.

    **Default:** `False`

`delete_preexisting_proc_dir`
:   specify if a pre-existing CDDS proc directory will be deleted when creating the CDDS directories.

    **Default:** `False`

`delete_preexisting_data_dir`
:   specify if a pre-existing CDDS data directory will be deleted when creating the CDDS directories.

    **Default:** `False`

## Examples

!!! example
    ```yaml
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
    override_cycling_frequency = ap7=P3M
    model_params_dir = /home/user/model_params.json
    continue_if_mip_convert_failed = False
    delete_preexisting_proc_dir = False
    delete_preexisting_data_dir = False
    ```