# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from dataclasses import dataclass

from cdds.common.mip_tables import MipTables
from cdds.common.request.request import Request
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator


@dataclass
class CheckCache:
    """
    Caches the request, the MIP tables and the controlled vocabulary validator
    """
    request: Request = None
    mip_tables: MipTables = None
    cv_validator: ControlledVocabularyValidator = None
