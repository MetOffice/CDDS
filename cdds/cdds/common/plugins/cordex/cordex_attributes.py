# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cordex_models` module contains the code required to
handle model parameters information for CORDEX models.
"""
from cdds.common.plugins.attributes import GlobalAttributes
from typing import Dict, Any


class CordexGlobalAttributes(GlobalAttributes):
    """
    Class to store and manage global attributes for CMIP6

    The request given in the init method will be validated if it contains
    all expected information that is need to handle the global attributes.
    """

    def __init__(self, request: Dict[str, Any]):
        super(CordexGlobalAttributes, self).__init__(request)

    def further_info_url(self) -> str:
        """
        Returns an empty further info url.

        :return: The further info url for CORDEX which is empty
        :rtype: str
        """
        return ''
