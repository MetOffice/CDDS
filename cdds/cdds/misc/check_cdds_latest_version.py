#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

"""Checks whether a newer CDDS environment is available. Logs accordingly."""

import re
from pathlib import Path
from typing import Tuple


def parse_version(version: str) -> Tuple[int, ...]:
    """Convert an 'X.Y.Z' version string to integer components."""
    return tuple(int(part) for part in version.split("."))


def retrieve_latest_version(environments_directory: Path) -> Tuple[int, ...]:
    """Return the highest version number from the conda_environments directory."""
    release_versions_available = []
    for environment in environments_directory.glob("cdds-*"):
        version_name = environment.name[len("cdds-"):]
        # Ignore non-release versions like '4.1.0rc1' or '4.2_dev-1'.
        if re.fullmatch(r"\d+\.\d+\.\d+", version_name):
            release_versions_available.append(parse_version(version_name))
    return max(release_versions_available)


def main_check_latest_version(version: str, central_environments_directory: Path) -> int:
    """Print a notice saying whether the activated CDDS version is the latest."""
    requested_version = parse_version(version)
    latest_version = retrieve_latest_version(central_environments_directory)

    if latest_version == requested_version:
        print("Latest version of CDDS activated.")
    elif latest_version > requested_version:
        print(
            "The latest version of CDDS is {}. \n"
            "You may have a valid reason for using version {}. "
            "However, upgrading is recommended to benefit from the latest features, fixes, and improvements."
            .format(".".join(map(str, latest_version)), version)
        )
    return 0
