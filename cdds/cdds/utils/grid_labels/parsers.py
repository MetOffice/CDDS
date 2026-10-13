# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import json
import re


def parse_mappings_json(mappings_file: str, plugin: str, realm: str) -> dict[str, str]:
    """Parse the mappings JSON file to extract grid names for a given plugin and realm.

    Parameters
    ----------
    mappings_file : str
        The path to the mappings JSON file.
    plugin : str
        The name of the plugin to filter the mappings for.
    realm : str
        The realm to filter the mappings for (e.g., "ocean" or "seaice").
    Returns
    -------
    dict[str, str]
        A dictionary mapping variable names to their corresponding grid names.
    """
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
