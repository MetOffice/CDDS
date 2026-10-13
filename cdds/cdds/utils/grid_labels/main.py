# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
from collections import defaultdict

from cdds.utils.grid_labels.mappings import Mapping
from cdds.utils.grid_labels.stashmaster import StashMasterRecord

GRID_NAME_TO_GRID_ID = {
    "latlon-native": {1, 2, 3, 4, 5, 26, 21, 17, 22},
    "latlon-uvgrid": {11, 12, 13, 14, 15},
    "latlon-ugrid": {18, 27},
    "latlon-vgrid": {19},
}

SUBSTREAM_TO_GRID_NAME = {
    "grid-T": "tripolar-native",
    "grid-U": "tripolar-ugrid",
    "grid-V": "tripolar-vgrid",
    "grid-W": "tripolar-native",
    "diaptr": "tripolar-native",
    "scalar": "tripolar-native",
    # for ukesmp13
    "ptrc-T": "tripolar-native",
    "diad-T": "tripolar-native",
}


GRID_TYPE = {
    "latlon-native": "atmos",
    "latlon-uvgrid": "atmos",
    "latlon-ugrid": "atmos",
    "latlon-vgrid": "atmos",
    "tripolar-ugrid": "ocean",
    "tripolar-vgrid": "ocean",
    "tripolar-native": "ocean",
    "tripolar-uvgrid": "ocean",
}


ANCILS = {
    "areacello_ti-u-hxy-u": "tripolar-native",
    "basin_ti-u-hxy-u": "tripolar-native",
    "deptho_ti-u-hxy-sea": "tripolar-native",
    "dxto_ti-u-hxy-u": "tripolar-native",
    "dxuo_ti-u-hxy-u": "tripolar-ugrid",
    "dxvo_ti-u-hxy-u": "tripolar-vgrid",
    "dyto_ti-u-hxy-u": "tripolar-native",
    "dyuo_ti-u-hxy-u": "tripolar-ugrid",
    "dyvo_ti-u-hxy-u": "tripolar-vgrid",
    "sftof_ti-u-hxy-u": "tripolar-native",
    "hfgeou_ti-u-hxy-sea": "tripolar-native",
    "hfsnthermds_tavg-ol-hxy-sea": "tripolar-native",
    "rsdo_tavg-ol-hxy-sea": "tripolar-native",
}
ANCILS_UKESM = {
    "agessc_tavg-ol-hxy-sea": "tripolar-native",
    "sf6_tavg-ol-hxy-sea": "tripolar-native",
    "sfdsi_tavg-u-hxy-sea": "tripolar-native",
    "prra_tavg-u-hxy-si": "tripolar-native",
    "sbl_tavg-u-hxy-si": "tripolar-native",
}

SEAICE_OVERRIDES = {
    "ukcm": {
        # all seaice variables are assumed to be tripolar-native unless specified here
        "sidmasstranx_tavg-u-hxy-u": "tripolar-ugrid",
        "sidmasstrany_tavg-u-hxy-u": "tripolar-vgrid",
        # these are seaice variable that will have their coordinates replaced by processor
        "sistrxdtop_tavg-u-hxy-si": "tripolar-ugrid",
        "sistrydtop_tavg-u-hxy-si": "tripolar-vgrid",
        "sistrxubot_tavg-u-hxy-si": "tripolar-ugrid",
        "sistryubot_tavg-u-hxy-si": "tripolar-vgrid",
        "siu_tavg-u-hxy-si": "tripolar-ugrid",
        "siv_tavg-u-hxy-si": "tripolar-vgrid",
        "siforceintstrx_tavg-u-hxy-si": "tripolar-ugrid",
        "siforceintstry_tavg-u-hxy-si": "tripolar-vgrid",
        "siforcetiltx_tavg-u-hxy-si": "tripolar-ugrid",
        "siforcetilty_tavg-u-hxy-si": "tripolar-vgrid",
        "siforcecoriolx_tavg-u-hxy-si": "tripolar-ugrid",
        "siforcecorioly_tavg-u-hxy-si": "tripolar-vgrid",
    },
    "ukesm1p3": {
        "sidmasstranx_tavg-u-hxy-u": "tripolar-uvgrid",
        "sidmasstrany_tavg-u-hxy-u": "tripolar-uvgrid",
        "sistrxdtop_tavg-u-hxy-si": "tripolar-uvgrid",
        "sistrydtop_tavg-u-hxy-si": "tripolar-uvgrid",
        "sistrxubot_tavg-u-hxy-si": "tripolar-uvgrid",
        "sistryubot_tavg-u-hxy-si": "tripolar-uvgrid",
        "siu_tavg-u-hxy-si": "tripolar-uvgrid",
        "siv_tavg-u-hxy-si": "tripolar-uvgrid",
        "siforceintstrx_tavg-u-hxy-si": "tripolar-uvgrid",
        "siforceintstry_tavg-u-hxy-si": "tripolar-uvgrid",
        "siforcetiltx_tavg-u-hxy-si": "tripolar-uvgrid",
        "siforcetilty_tavg-u-hxy-si": "tripolar-uvgrid",
        "siforcecoriolx_tavg-u-hxy-si": "tripolar-uvgrid",
        "siforcecorioly_tavg-u-hxy-si": "tripolar-uvgrid",
    },
}


def grid_ids_to_grid_name(ids: set[int]) -> str | None:
    """Convert a set of grid IDs to a grid name.

    Parameters
    ----------
    ids : set[int]
        A set of grid IDs to be converted.

    Returns
    -------
    str | None
        The corresponding grid name if found, otherwise None.
    """
    for label, label_ids in GRID_NAME_TO_GRID_ID.items():
        if ids.issubset(label_ids):
            return label
    return None


def stash_to_grid_name(mapping: Mapping, records: dict) -> str:
    """
    Convert a mapping's stash codes to a grid name using the provided STASH records.

    Parameters
    ----------
    mapping : Mapping
        The mapping object containing stash codes.
    records : dict
        A dictionary of STASH records.
    Raises
    ------
    ValueError
        If no corresponding grid name can be found for the given mapping and stash codes.

    Returns
    -------
    str
        The corresponding grid name.
    """
    grid_ids = {int(records[code].Grid) for code in mapping.stash}
    if grid_name := grid_ids_to_grid_name(grid_ids):
        return grid_name
    else:
        raise ValueError(
            f"Failed to find grid name for mapping: {mapping.name}, MIP Table: {mapping.mip_table}, "
            f"Stash codes: {mapping.stash}, Grid ids: {grid_ids}"
        )


def map_variables_to_grid_names(
    mappings: dict[str, Mapping],
    ocean_grids: dict[str, str],
    seaice_grids: dict[str, str],
    records: dict[str, StashMasterRecord],
    plugin: str,
) -> dict[str, dict[str, tuple[str, str]]]:
    """Map variables to their corresponding grid names.

    Parameters
    ----------
    mappings : dict[str, Mapping]
        A dictionary mapping variable names to their corresponding Mapping objects.
    ocean_grids : dict[str, str]
        A dictionary mapping ocean variable names to their corresponding substream names.
    seaice_grids : dict[str, str]
        A dictionary mapping sea ice variable names to their corresponding substream names.
    records : dict
        A dictionary of STASH records.
    plugin : str
        The name of the plugin.

    Returns
    -------
    dict[str, dict[str, tuple[str, str]]]
        A dictionary mapping MIP table names to dictionaries, which map variable names to tuples containing the grid
        type and grid name.
    """
    grid_names = defaultdict(dict)

    for variable, mapping in mappings.items():
        grid_name = None

        if mapping.stash:
            grid_name = stash_to_grid_name(mapping, records)
        elif variable in ocean_grids:
            grid_name = SUBSTREAM_TO_GRID_NAME[ocean_grids[variable]]
        elif variable in ANCILS:
            grid_name = ANCILS[variable]
        elif variable in seaice_grids and variable not in SEAICE_OVERRIDES[plugin]:
            grid_name = "tripolar-native"
        elif variable in SEAICE_OVERRIDES[plugin]:
            grid_name = SEAICE_OVERRIDES[plugin][variable]

        if not grid_name:
            print(f"{plugin} Failed to identify a grid name for variable: {variable}, MIP Table: {mapping.mip_table}")
        else:
            grid_names[mapping.mip_table][variable] = (GRID_TYPE[grid_name], grid_name)

    return grid_names


def write_grid_names_config(grid_names: dict[str, dict[str, tuple[str, str]]], output_file: str) -> None:
    """Write the grid names to a file.

    Parameters
    ----------
    grid_names : dict[str, dict[str, tuple[str, str]]]
        A dictionary mapping MIP table names to dictionaries, which map variable names to tuples containing the grid
        type and grid name.
    output_file : str
        The path to the output configuration file.
    """
    with open(output_file, "w") as fh:
        for mip_table, variables in grid_names.items():
            fh.write(f"[{mip_table}]\n")
            for variable, (grid_type, grid_name) in variables.items():
                fh.write(f"{variable} = {grid_type} {grid_name}\n")
            fh.write("\n")
