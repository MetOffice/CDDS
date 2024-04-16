# Common Section

The `common` section in the request configuration contains common setting like the path to the root data folder or 
the path to the external plugin.

## Configuration Values

`external_plugin`
:   module path to external CDDS plugin, e.g. `cdds_arise.arise_plugin`

`external_plugin_location`
:   path to the external plugin implementation, e.g. `/home/h03/cdds/arise`

`mip_table_dir`
:   path to the directory containing the inforamtion about the MIP tables, e.g. `/home/h03/cdds/etc/mip_tables/CMIP6/01.00.29/`

    **Default:** The path to the MIP table directoring specified in the corresponding plugin

`mode`
:   mode that should be used to CMORised the data - `strict` or `relaxed`. If mode is `strict`, CMOR will fail if there 
    are warnings regarding compliance of CMOR standards. If mode is `relaxed`, CMOR will only fail if cubes present serve 
    discrepancies with CMOR standards.

    **Default:** `strict`

`package`
:   package name used to distinguish different run throughs of CDDS, e.g. `round-1`.

`workflow_basename`
:   name of the workflow name of the CDDS suite that will trigger during the CDDS processing suite

    **Default**: `<model_id>_<experiment_id>_<variant_label>` - all three values are defined in the `metadata` section

`root_proc_dir`
:   root path to the `proc` directory where the non-data outputs are written, e.g. log files.

`root_data_dir`
:   root path to the `data` directory where the output files of the model are written to.

`root_ancil_dir`
:   root path to the location of the ancillary files. The files should be located in a sub-directory of this path 
    with the name of the model ID.

    **Default:** Path to the directory containing the ancillary files located in the CDDS home directory

`root_hybrid_heights_dir`
:   root path to the location of the hybrid heights files.

    **Default::** Path to the directory containing hybrid heights files located in the CDDS home directory

`root_replacement_coordinates_dir`
:   root path to the location of the replacement coordinates files.

    **Default:** Path to the directory containing the replacement coordinates files located in the CDDS home directory

`sites_files`
:   path to the file containing the sites information.

    **Default:** Path to the file containing the site information located in the CDDS home directory

`standard_names_dir`
:   the directory containing the standard names that should be used.

    **Default**: Path to the standard names directory located in the CDDS home directory

`standard_names_version`
:   the version of the standard name directory that should be used.

    **Default:** `latest`

`simulation`
:   if set to `True` CDDS operation will be simulated

`log_level`
:   identify which log level should be used for logging - `CRITICAL`, `INFO` or `DEBUG`

    **Default:** `INFO`

## Examples

!!! example
    ```yaml
    [common]
    external_plugin =
    external_plugin_location =
    mip_table_dir = /home/h03/cdds/etc/mip_tables/CMIP6/01.00.29/
    mode = strict
    package = round-1-part-1
    workflow_basename = UKESM1-0-LL_historical_r1i1p1f2
    root_proc_dir = /project/user/proc
    root_data_dir = /project/user/cdds_data
    root_ancil_dir = /home/h03/cdds/etc/ancil/
    root_hybrid_heights_dir = /home/h03/cdds/etc/vertical_coordinates/
    root_replacement_coordinates_dir = /home/h03/cdds/etc/horizontal_coordinates/
    sites_file = /home/h03/cdds/etc/cfmip2/cfmip2-sites-orog.txt
    simulation = False
    log_level = INFO
    ```
