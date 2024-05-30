# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The :mod:`cordex_models` module contains the code required to
handle model parameters information for CORDEX models.
"""
from cdds.common.plugins.attributes import GlobalAttributes
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cdds.common.request.request import Request


class CordexGlobalAttributes(GlobalAttributes):
    """
    Class to store and manage global attributes for CORDEX

    The request given in the init method will be validated if it contains
    all expected information that is need to handle the global attributes.
    """

    def __init__(self, request: 'Request'):
        super(CordexGlobalAttributes, self).__init__(request)

    def further_info_url(self) -> str:
        """
        Returns an empty further info url.

        :return: The further info url for CORDEX which is empty
        :rtype: str
        """
        return ''
