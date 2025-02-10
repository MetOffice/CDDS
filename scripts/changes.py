# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""Generate changelog pages on the fly."""

from pathlib import Path

import mkdocs_gen_files


def generate_changes():
    packages = ["cdds", "mip_convert"]
    for package in packages:
        package_path = Path(__file__).parent.parent / package / "CHANGES.md"
        filename = f"changes_{package}.md"

        with mkdocs_gen_files.open(filename, "w") as f:
            with open(package_path, "r") as fh:
                for line in fh.readlines():
                    print(f"{line}", file=f)

generate_changes()
