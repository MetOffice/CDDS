# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""Generate changes"""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

def generate_changes():
    packages = ["cdds", "mip_convert"]
    for package in packages:
        package_path = Path(__file__).parent.parent / package / "CHANGES.md"
        filename = f"changes_{package}.md"

        with mkdocs_gen_files.open(filename, "w") as f:
            with open(package_path, "r") as fh:
                for line in fh.readlines():
                    print(f"{line}", file=f)

        mkdocs_gen_files.set_edit_path(filename, "gen_pages.py")

generate_changes()
