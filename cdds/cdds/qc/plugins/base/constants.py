# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.md for license details.
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
