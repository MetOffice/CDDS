# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.

SOURCE_REGEX = r"^([a-zA-Z\d\-_\.\s]+) \(\d{4}\)"

CF_CONVENTIONS = ["CF-1.7", "CF-1.7 CMIP-6.2", "CF-1.7 CMIP-6.2 UGRID-1.0"]

MANDATORY_TEXT_ATTRIBUTES = [
    "grid",
]

OPTIONAL_TEXT_ATTRIBUTES = [
    "history",
    "references",
    "title",
    "variant_info",
    "contact",
    "comment",
]

PARENT_ATTRIBUTES = [
    "branch_method",
    "parent_activity_id",
    "parent_experiment_id",
    "parent_mip_era",
    "parent_source_id",
    "parent_time_units",
    "parent_source_id",
]

MISSING_VALUE = 1.e+20
