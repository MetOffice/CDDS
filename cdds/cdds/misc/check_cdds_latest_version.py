#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

"""Checks whether a newer CDDS environment is available. Logs accordingly."""

import re
import sys
from pathlib import Path
from typing import Optional, Tuple


def parse_input_version(version: str) -> Optional[Tuple[int, ...]]:
    """Return a cdds 'X.Y.Z' version as integers, or None for any other format e.g.3.0.5rc1."""
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        return None
    return tuple(int(part) for part in version.split("."))


def retrieve_latest_version(environments_directory: Path) -> Optional[Tuple[int, ...]]:
    """Return the highest version number from the conda_environments directory."""
    versions_available = []
    for environment in environments_directory.glob("cdds-*"):
        version = parse_input_version(environment.name[len("cdds-"):])
        if version is not None:
            versions_available.append(version)
    return max(versions_available, default=None)


def main(version: str, environments_directory: Path) -> int:
    """Print a notice saying whether the activated CDDS version is the latest."""
    requested_version = parse_input_version(version)
    latest_version = retrieve_latest_version(environments_directory)
    if requested_version is None or latest_version is None:
        return 0

    if latest_version == requested_version:
        print("Latest version of CDDS activated")
    elif latest_version > requested_version:
        print(
            "The latest version of cdds is {}. You may have a valid reason for using version {}. "
            "However, upgrading is recommended to benefit from the latest features, fixes, and improvements."
            .format(".".join(map(str, latest_version)), version)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], Path(sys.argv[2])))
