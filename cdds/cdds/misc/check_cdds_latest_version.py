#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

"""Checks for the latest version of CDDS when source setup_env_for_cdds X.Y.X is used.
Logs appropriately if latest version has not been activated."""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Tuple


RELEASE_VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")


def parse_version(version: str) -> Tuple[int, ...]:
    """Convert an 'X.Y.Z' version string to integer components."""
    return tuple(int(part) for part in version.split("."))


def retrieve_latest_version(environments_directory: Path) -> Tuple[int, ...]:
    """Return the highest version number from the conda_environments directory."""
    release_versions_available = []
    for environment in environments_directory.glob("cdds-*"):
        version_name = environment.name[len("cdds-"):]
        # Ignore non-release versions like '4.1.0rc1' or '4.2_dev-1'.
        if RELEASE_VERSION_PATTERN.fullmatch(version_name):
            release_versions_available.append(parse_version(version_name))
    return max(release_versions_available)


def check_latest_version(version: str, central_environments_directory: Path) -> int:
    """Print a notice saying whether the activated CDDS version is the latest."""
    if not RELEASE_VERSION_PATTERN.fullmatch(version):
        print("Unexpected version selected. Double check {} was the version you meant to activate.".format(version))
        return 0

    requested_version = parse_version(version)
    latest_version = retrieve_latest_version(central_environments_directory)

    if latest_version == requested_version:
        print("Latest version of CDDS activated.".format(version))
    elif latest_version > requested_version:
        print(
            "The latest version of CDDS is {}. \n"
            "You may have a valid reason for using version {}. "
            "However, upgrading is recommended to benefit from the latest features, fixes, and improvements."
            .format(".".join(map(str, latest_version)), version)
        )
    return 0


def main() -> int:
    """Check whether the active CDDS environment is the latest available version."""
    parser = argparse.ArgumentParser(
        description=(
            "Check whether the active CDDS environment is the latest version available "
            "alongside it in the central conda environments directory."
        )
    )
    parser.parse_args()

    active_environment = Path(os.environ.get("CONDA_PREFIX", sys.prefix))
    if not active_environment.name.startswith("cdds-"):
        parser.error("unable to determine the active CDDS environment from {}".format(active_environment))

    version = active_environment.name[len("cdds-"):]
    return check_latest_version(version, active_environment.parent)
