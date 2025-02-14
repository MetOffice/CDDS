# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os

from dataclasses import dataclass
from typing import List, Dict, Any

from cdds.common.constants import DATA_DIR_FACET_STRING, INPUT_DATA_DIRECTORY, PROC_DIRECTORY_FACET_STRING
from cdds.common import construct_string_from_facet_string


@dataclass
class SetupConfig:
    """
    Store information that is needed to generate the variable list.
    """
    test_base_dir: str = None
    request_cfg: str = None
    package: str = None
