# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import json
import re


def parse_ocean_grids(ocean_grids_file: str) -> dict[str, str]:
    with open(ocean_grids_file, "r") as fh:
        data = fh.readlines()

    ocean_grids = {}
    for line in data:
        variable, grid = line.strip().split(":")
        ocean_grids[variable] = grid

    return ocean_grids


def parse_icemod_grids(icemod_grids_file: str) -> dict[str, str]:
    with open(icemod_grids_file, "r") as fh:
        data = fh.readlines()

    icemod_grids = {}

    regex = r"float (.*)\(.*(grid_\w)"

    for line in data:
        match = re.search(regex, line)
        if match:
            variable = match.group(1)
            grid = match.group(2)
            icemod_grids[variable] = grid.replace("_", "-")
    return icemod_grids


def parse_mappings_json(mappings_file: str, plugin: str, realm: str) -> dict[str, str]:
    with open(mappings_file, "r") as fh:
        mappings = json.load(fh)

    model_alias = {"ukcm2": "UKCM2", "ukesm1p3": "UKESM1-3"}

    mappings = [mapping for mapping in mappings if mapping["XIOS entries"]]

    grids = {}

    if realm == "ocean":
        regex = re.compile(r"^o\w{2}/([\w-]*)")
    elif realm == "seaice":
        regex = re.compile(r"^(i\w{2})")

    for mapping in mappings:
        if model_alias[plugin] in mapping["XIOS entries"]:
            match = regex.match(mapping["XIOS entries"][model_alias[plugin]])
            if match:
                grids[mapping["Data Request information"]["Branded variable name"]] = match.group(1)

    return grids
