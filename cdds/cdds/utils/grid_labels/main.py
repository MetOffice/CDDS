# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
from collections import defaultdict

from cdds.utils.grid_labels.mappings import Mapping
from cdds.utils.grid_labels.parsers import parse_icemod_grids, parse_ocean_grids
from cdds.utils.grid_labels.stashmaster import stash_records

grid_name_to_grid_id = {
    "latlon-native": {1, 2, 3, 4, 5, 26, 21, 17, 22},
    "latlon-uvgrid": {11, 12, 13, 14, 15},
    "latlon-ugrid": {18, 27},
    "latlon-vgrid": {19},
}

substream_to_grid_name = {
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


grid_type = {
    "latlon-native": "atmos",
    "latlon-uvgrid": "atmos",
    "latlon-ugrid": "atmos",
    "latlon-vgrid": "atmos",
    "tripolar-ugrid": "ocean",
    "tripolar-vgrid": "ocean",
    "tripolar-native": "ocean",
    "seaice-native": "ocean",
}


ancils = {
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

seaice = {
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
}


def grid_ids_to_grid_name(ids: set[int]) -> str | None:
    for label, label_ids in grid_name_to_grid_id.items():
        if ids.issubset(label_ids):
            return label
    return None


def stash_to_grid_name(mapping, records):
    grid_ids = {int(records[code].Grid) for code in mapping.stash}
    if grid_name := grid_ids_to_grid_name(grid_ids):
        return grid_name
    else:
        raise ValueError(
            f"Failed to find grid name for mapping: {mapping.name}, MIP Table: {mapping.mip_table}, Stash codes: {mapping.stash}, Grid ids: {grid_ids}"
        )


def map_variables_to_grid_names(mappings: dict[str, Mapping], ocean_grids, seaice_grids, records, plugin):
    grid_names = defaultdict(dict)

    for variable, mapping in mappings.items():
        grid_name = None

        if mapping.stash:
            grid_name = stash_to_grid_name(mapping, records)
        elif variable in ocean_grids:
            grid_name = substream_to_grid_name[ocean_grids[variable]]
        elif variable in ancils:
            grid_name = ancils[variable]
        # ukcm2 seaice
        elif plugin == "ukcm2":
            if variable in seaice_grids and variable not in seaice:
                grid_name = "tripolar-native"
            if variable in seaice:
                grid_name = seaice[variable]
        # ukesm1p3 seaice
        elif plugin == "ukesm1p3":
            if variable in seaice_grids:
                grid_name = "seaice-native"

        if not grid_name:
            print(f"{plugin} Failed to identify a grid name for variable: {variable}, MIP Table: {mapping.mip_table}")
        else:
            grid_names[mapping.mip_table][variable] = (grid_type[grid_name], grid_name)

    return grid_names


def write_grid_names_config(grid_names: dict[str, dict[str, tuple[str, str]]], output_file: str) -> None:
    with open(output_file, "w") as fh:
        for mip_table, variables in grid_names.items():
            fh.write(f"[{mip_table}]\n")
            for variable, (grid_type, grid_name) in variables.items():
                fh.write(f"{variable} = {grid_type} {grid_name}\n")
            fh.write("\n")
