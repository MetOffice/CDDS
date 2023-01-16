# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from cdds.common.plugins.attributes import GlobalAttributes
from typing import Dict, Any


class CordexGlobalAttributes(GlobalAttributes):

    def __init__(self, request: Dict[str, Any]):
        super(CordexGlobalAttributes, self).__init__(request)

    def further_info_url(self) -> str:
        return ''
