# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
from dataclasses import dataclass

from cdds.common.mip_tables import MipTables
from cdds.common.request.request import Request
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator
from cdds.qc.common import GlobalAttributesCache


@dataclass
class CheckCache:
    """
    Caches the request, the MIP tables and the controlled vocabulary validator
    """
    request: Request = None
    mip_tables: MipTables = None
    cv_validator: ControlledVocabularyValidator = None
    global_attributes: GlobalAttributesCache = None
