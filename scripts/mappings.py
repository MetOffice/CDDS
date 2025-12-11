# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""Generate mappings pages on the fly."""

import os
import os.path

import mkdocs_gen_files
from cdds.common.mappings_viewer.constants import FOOTER, HEADER
from cdds.common.mappings_viewer.mappings_viewer import build_table, get_mappings
from cdds.versions import get_version
from mip_convert.plugins.plugin_loader import find_internal_plugin, load_mapping_plugin

models = {
    "HadGEM3": "vn13.1",
    "HadGEM3GC5": "vn13.1",
    "HadREM-CP4A": "vn13.1",
    "HadREM3": "vn13.1",
    "UKESM1": "vn13.1",
}


def main():
    """Main function for generating the mappings html pages."""
    for model, stash_version in models.items():
        stash_path = os.path.expandvars(f"$UMDIR/{stash_version}/ctldata/STASHmaster/STASHmaster-meta.conf")
        load_mapping_plugin(model)
        plugin = find_internal_plugin(model)

        mappings_dir = plugin.mapping_data_dir
        mappings = get_mappings(mappings_dir)
        table = build_table(mappings, mappings_dir, stash_path)

        html = (
            HEADER
            + "<h2>Variable Mappings for {} (Created with CDDS v{})</h2>".format(model, get_version("cdds"))
            + "<h2>STASHmaster {}".format(stash_version)
            + "<p> </p>"
            + '<p>Use the search box to filter rows, e.g. search for "tas" or "Amon tas".</p>'
            + table
            + FOOTER
        )

        with mkdocs_gen_files.open(f"mappings/{model}.html", "w") as f:
            for line in html.split("\\n"):
                print(f"{line}", file=f)

    with mkdocs_gen_files.open("mappings/index.md", "w") as f:
        for model in models.keys():
            print(f"- [{model}]({model}.html)", file=f)


main()
