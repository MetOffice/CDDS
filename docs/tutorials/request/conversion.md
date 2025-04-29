# Conversion Section

The `conversion` in the request configuration contains settings that specify how CDDS is run.

## Configuration Values

`mip_convert_plugin`
:   specify the id of the MIP convert plugin that should be used. This value is required for running MIP convert!

`mip_convert_external_plugin`
:   module path to external MIP convert plugin, e.g. `cdds_arise.arise_mip_convert_plugin`. This must not be set if an internal plugin is used.

`mip_convert_external_plugin_location`
:   full path to the external MIP convert plugin implementation, e.g. `$CDDS_ETC/mapping_plugins/arise`. This must not be set if an internal MIP convert plugin is used.

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

`slicing`
:   slicing period for specified stream. Each stream should be specified along with the slicing period using the format
    `<stream>=<period>`, e.g. `ap7=year ap8=month`. Only, `year` and `month` as period are supported.

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
    mip_convert_plugin = HadGEM3
    mip_convert_external_plugin =
    mip_convert_external_plugin_location =
    skip_extract = False
    skip_extract_validation = False
    skip_configure = False
    skip_qc = False
    skip_archive = False
    cylc_args = -v
    no_email_notifications = True
    scale_memory_limits = 
    override_cycling_frequency = ap7=P3M
    model_params_dir = /home/user/model_params.json
    continue_if_mip_convert_failed = False
    delete_preexisting_proc_dir = False
    delete_preexisting_data_dir = False
    ```