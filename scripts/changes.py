# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.rst for license details.
"""Generate changelog pages on the fly."""

from pathlib import Path

import mkdocs_gen_files


def generate_changes():
    """ Generates a CHANGES.md page from the corresponding file in the cdds/mip_convert packages.
    See https://oprypin.github.io/mkdocs-gen-files/index.html for API usage examples.
    """
    packages = ["cdds", "mip_convert"]
    for package in packages:
        package_path = Path(__file__).parent.parent / package / "CHANGES.md"
        filename = f"changes_{package}.md"

        with mkdocs_gen_files.open(filename, "w") as f:
            with open(package_path, "r") as fh:
                for line in fh.readlines():
                    print(f"{line}", file=f)


generate_changes()
