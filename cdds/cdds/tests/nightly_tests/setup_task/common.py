# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
    input_data: str = None
    package: str = None
