# Update Model Parameters JSON File

## Stream File Frequencies

The `stream_file_frequency` section contains a key value pairs where the key the frequency is and the value the list of 
streams. Following frequencies are supported: `hourly`, `daily`, `10 day`, `quarterly`, `monthly`

??? example
    Assuming `ap4` and `ap5` are monthly streams and `ap6` is a `daily` stream:
    ```json
    "stream_file_frequency": {
       "monthly": [
           "ap4",
           "ap5"
       ],
       "daily": [
          "ap6"
       ]
    }
    ```

## Cylc length / Memory / Temporary space

There are following three sections that have an entry for each stream:

`cylc_length`
:   lengths of the suite cylc for each stream
    ??? example
        ```json
        "cycle_length": {
            "ap4": "P5Y",
            "ap5": "P5Y",
            "ap6": "P1Y"
        }
        ```

`memory`
:   memory usages of each stream

    !!! note
        This is the starting point for memory and adaptive memory, storage and time limits are used.

    ??? example
        ```json
        "memory": {
            "ap4": "12G",
            "ap5": "8G",
            "ap6": "30G"
        }
        ```

`temp_space`
:   temporary space of each stream

    !!! note
        This is the starting point for memory and adaptive memory, storage and time limits are used.

    ??? example
        ```json
        "temp_space": {
            "ap4": 98304,
            "ap5": 40960,
            "ap6": 98304
        }
        ```

## Sizing information

The entry `sizing_info` represents the sizing information and has JSON objects represent the information as value. Each 
JSON object has as key the frequency and as value the shape with its coordinates.

!!! note
    The frequency is the global attribute from the files being concatenated.

??? example
    ```json
    "sizing_info": {
        "mon": {
            "default": 100,
            "85-144-192": 50,
            "85-145-192": 50,
            "86-144-192": 50,
            "75-330-360": 50
        },
        "monPt": {
            "default": 100,
            "85-144-192": 50,
            "85-145-192": 50,
            "86-144-192": 50,
            "75-330-360": 50
        }
    }
    ```

## Sub daily streams

There are one entry for the subdaily streams `subdaily_streams` that contains an array of subdaily streams.

??? example
    ```json
    "subdaily_streams": [
        "ap6",
        "ap7",
        "ap8",
        "ap9",
        "apt"
    ]
    ```

`halo_removal`
:   The size of haloes to be stripped from the specified streams.

??? example
    ```json
    "halo_removal": {
        "onm": {
            "longitude": "1:-1",
            "latitude": "1:-1"
        },
        "ond": {
            "longitude": "1:-1",
            "latitude": "1:-1"
        }
    },
    ```

## Grid information

There are two supported grids - atmosphere and ocean. The entries are `atoms` and `ocean`.

### Atmosphere Grid Information

Following information should be provided:

`atmos_timestep`
:   the atmosphere timestep. The timestep is often different for different model resolutions.

`model_info`
:   a simple description of the grid, e.g. `N96 grid`. It is interpolated into `grid attribute`.

`nominal_resolution`
:   the nominal resolution. This needs to agree with the Controlled Vocabulary for the project.

`longitude`
:   the number of longitude points in the atmosphere grid

`latitude`
:   the number of latitude points in the atmosphere grid (T points and U points)

`v_latitude`
:   The number of latitude points on the atmosphere grid for data on V points

`levels`
:   the number of vertical levels

`ancil_filenames`
:   the ancillary file names. These are looked for in the directory `<root_ancil_dir>/<source_id>` as specified in the 
    request config file

`hybrid_heights_files`
:   the hybrid heights files

??? example
    ```json
    "atmos": {
      "atmos_timestep": 1200,
      "model_info": "N96 grid",
      "nominal_resolution": "250 km",
      "longitude": 192,
      "latitude": 144,
      "v_latitude": 145,
      "levels": 85,
      "ancil_filenames": [
        "qrparm.landfrac.pp",
        "qrparm.soil.pp"
      ],
      "hybrid_heights_files": [
        "atmosphere_theta_levels_85.txt",
        "atmosphere_rho_levels_86.txt"
      ]
    }
    ```

### Ocean Grid Information

Following information should be provided:

`model_info`
:   a simple description of the grid, e.g. `N96 grid`. It is interpolated into `grid attribute`.

`nominal_resolution`
:   the nominal resolution. This needs to agree with the Controlled Vocabulary for the project.

`longitude`
:   the number of longitude points in the ocean grid

`latitude`
:   the number of latitude points in the ocean grid (T points and U points)

`v_latitude`
:   the number of latitude points on the ocean grid for data on V points

`levels`
:   the number of vertical levels

`ancil_filenames`
:   the ancillary file names. These are looked for in the directory `<root_ancil_dir>/<source_id>` as specified in the 
    request config file

`replacement_coordinates_file`
:   the replacement coordinates file for CICE model output

`hybrid_heights_files`
:   the hybrid heights files.

    !!! note
        This is not relevant for the ocean, but still needs to be present.

`bounds_coordinates` (Optional, added in CDDS v3.1.0)
:   This field is a dictionary containing the list of netCDF variables that correspond to the bounds variables for
    coordinates in the NEMO output files for each ocean substream. If this is not specified the built in defaults 
    will be used.

`masked`
:   a json object of ocean grid polar masks for the grid. Each masked entry as a grid label and its masked value split 
    by the `slice_latitude` and `slice_longitude`. These are used to mask duplicate cells along the polar rows.

    ??? example
        ```json
        "masked": {
            "grid-V": {
                "slice_latitude": [
                    -1,
                    null,
                    null
                ],
                "slice_longitude": [
                    180,
                    null,
                    null
                ]
            }
        }
        ```

## Example
!!! example
    ```json
    {
        "stream_file_frequency": {
            "monthly": [
                "ap4",
                "ap5"
            ],
            "10 day": [
            "ap6"
        ]
        },
        "cycle_length": {
            "ap4": "P5Y",
            "ap5": "P5Y",
            "ap6": "P1Y"
        },
        "memory": {
            "ap4": "12G",
            "ap5": "8G",
            "ap6": "30G"
        },
        "temp_space": {
            "ap4": 98304,
            "ap5": 40960,
            "ap6": 98304
        },
        "sizing_info": {
            "mon": {
                "default": 100,
                "85-144-192": 50,
                "85-145-192": 50,
                "86-144-192": 50,
                "75-330-360": 50
            },
            "day": {
                "default": 20,
                "144-192": 100,
                "19-144-192": 20
            },
        },
        "subdaily_streams": [
            "ap6"
        ],
        "grid_info": {
            "atmos": {
                "atmos_timestep": 1200,
                "model_info": "N96 grid",
                "nominal_resolution": "250 km",
                "longitude": 192,
                "latitude": 144,
                "v_latitude": 145,
                "levels": 85,
                "ancil_filenames": [
                    "qrparm.landfrac.pp",
                    "qrparm.soil.pp"
                ],
                "hybrid_heights_files": [
                    "atmosphere_theta_levels_85.txt",
                    "atmosphere_rho_levels_86.txt"
                ]
            },
            "ocean": {
                "model_info": "eORCA1 tripolar primarily 1 deg with meridional refinement down to 1/3 degree in the tropics",
                "nominal_resolution": "100 km",
                "longitude": 360,
                "latitude": 330,
                "levels": 75,
                "replacement_coordinates_file": "cice_eORCA1_coords.nc",
                "ancil_filenames": [
                    "ocean_constants.nc",
                    "ocean_byte_masks.nc",
                    "ocean_basin.nc",
                    "diaptr_basin_masks.nc",
                    "ocean_zostoga.nc"
                ],
                "bounds_coordinates": {
                    "onm-grid-T": ["bounds_nav_lon", "bounds_nav_lat", "time_centered_bounds", "deptht_bounds"]
                },
                "hybrid_heights_files": [],
                "masked": {
                    "grid-V": {
                        "slice_latitude": [
                        -1,
                        null,
                        null
                        ],
                        "slice_longitude": [
                            180,
                            null,
                            null
                        ]
                    },
                    "cice-U": {
                        "slice_latitude": [
                            -1,
                            null,
                            null
                        ]
                    }
                }
            }
        }
    }
    ```

## Check Model Parameters JSON File

There is a little tool, that checks the basic of your model parameters file:
```commandline
validate_model_params <request file>
```
where the `<request file>` is the path to your request that uses your model parameters JSON file.