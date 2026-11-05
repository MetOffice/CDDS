#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

"""Check whether activated CDDS environment is the latest available release.

Run by ``setup_env_for_cdds`` to notify users when a newer CDDS release is available.
"""

import re
import sys
from pathlib import Path
from typing import Tuple


RELEASE_VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")
CENTRAL_ENVIRONMENTS_DIRECTORY = Path("~cdds/conda_environments").expanduser()


def parse_version(version: str) -> Tuple[int, ...]:
    """Convert a release version string into integer components.

    Parameters
    ----------
    version : str
        Version string in ``X.Y.Z`` format.

    Returns
    -------
    tuple of int
        Numeric version components.
    """
    return tuple(int(part) for part in version.split("."))


def retrieve_latest_version(environments_directory: Path) -> Tuple[int, ...]:
    """Find the highest release version in the target directory.

    Parameters
    ----------
    environments_directory : pathlib.Path
        Directory containing CDDS environment directories.

    Returns
    -------
    tuple of int
        Numeric components of the highest release version.

    Raises
    ------
    ValueError
        If the directory contains no release-version environments.
    """
    release_versions_available = []
    for environment in environments_directory.glob("cdds-*"):
        version_name = environment.name[len("cdds-"):]
        # Ignore non-release versions like '4.1.0rc1' or '4.2_dev-1'.
        if RELEASE_VERSION_PATTERN.fullmatch(version_name):
            release_versions_available.append(parse_version(version_name))
    return max(release_versions_available)


def check_latest_version(version: str, central_environments_directory: Path) -> int:
    """Print a notice describing how the activated release compares to latest release.

    Parameters
    ----------
    version : str
        Version of the activated CDDS environment.
    central_environments_directory : pathlib.Path
        Directory containing centrally installed CDDS environments.

    Returns
    -------
    int
        Zero after printing the applicable notice.
    """
    if not RELEASE_VERSION_PATTERN.fullmatch(version):
        print("Unexpected version selected. Double check {} was the version you meant to activate.".format(version))
        return 0

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


if __name__ == "__main__":
    # Run by setup_env_for_cdds as:
    # python -m cdds.misc.check_latest_version_available <version>
    sys.exit(check_latest_version(sys.argv[1], CENTRAL_ENVIRONMENTS_DIRECTORY))
