# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
from dataclasses import dataclass
from typing import TYPE_CHECKING
from cdds.common.mip_tables import MipTables
from cdds.common.request.request import Request
from cdds.qc.common import GlobalAttributesCache
if TYPE_CHECKING:
    from cdds.qc.plugins.cmip6.validators import Cmip6CVValidator
    from cdds.qc.plugins.cordex.validators import CordexCVValidator


@dataclass
class CheckCache:
    """Caches the request, the MIP tables and the controlled vocabulary validator"""
    request: Request = None
    mip_tables: MipTables = None
    cv_validator: 'CordexCVValidator | Cmip6CVValidator' = None
    global_attributes: GlobalAttributesCache = None
