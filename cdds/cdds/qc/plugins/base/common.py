# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from dataclasses import dataclass

from cdds.common.mip_tables import MipTables
from cdds.common.request import Request
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator


@dataclass
class CheckCache:
    request: Request = None
    mip_tables: MipTables = None
    cv_validator: ControlledVocabularyValidator = None
