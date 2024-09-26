# Miscellany Section

The `misc` in the request configuration contains any settings that do not fit in any other section.

## Configuration Values

`atmos_timestep`
:   atmospheric time step in seconds

    **Default:** The atmospheric time step that the current loaded plugin is provided.

`use_proc_dir`
:   write log files to the appropriate component directory in the proc directory as defined by the common section in the 
    request configuration.

    **Default:** `True`

`no_overwrite`
:   do not overwrite files in data directory defined by the common section in the request configuration.

    **Default:** `False`

`halo_removal_latitude`
:   number of latitude points to be stripped using `<start>:<stop>` as the format.

`halo_removal_longitude`
:   number of longitude points to be stripped using `<start>:<stop>` as the format.

!!! example
    Strip 5 points at the start and end for latitude and strip 10 points at the start and end
    for longitude:
    ```yaml
    halo_removal_latitude = 5:-5
    halo_removal_longitude = 10:-10
    ```

## Examples

!!! example
    ```yaml
    [misc]
    atmos_timestep = 900
    use_proc_dir = True
    no_overwrite = False
    halo_removal_latitude = 5:-5
    halo_removal_longitude = 10:-10
    ```
