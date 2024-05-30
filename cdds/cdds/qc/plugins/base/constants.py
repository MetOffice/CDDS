# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from typing import List


CV_ATTRIBUTES: List[str] = [
    "experiment_id",
    "frequency",
    "grid_label",
    "institution_id",
    "realm",
    "source_id",
    "sub_experiment_id",
    "nominal_resolution",
    "table_id",
]

PARENT_ATTRIBUTES: List[str] = [
    "branch_method",
    "parent_activity_id",
    "parent_experiment_id",
    "parent_mip_era",
    "parent_source_id",
    "parent_time_units",
    "parent_source_id",
]
