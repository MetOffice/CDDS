# (C) British Crown Copyright 2022-2024, Met Office.
# Please see LICENSE.rst for license details.
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cdds.common.request.request import Request


class GlobalAttributes(object, metaclass=ABCMeta):
    """
    Abstract class to store and manage global attributes of a plugin
    """

    def __init__(self, request: 'Request') -> None:
        self._request: 'Request' = request

    @abstractmethod
    def further_info_url(self) -> str:
        """
        Returns the further info url according the global attributes values.

        :return: The further info url
        :rtype: str
        """
        pass


class DefaultGlobalAttributes(GlobalAttributes):
    """
    Default global attributes for plugins.
    """

    def __init__(self, request: 'Request' = None) -> None:
        super(DefaultGlobalAttributes, self).__init__(request)

    def further_info_url(self) -> str:
        """
        Returns the further info url. Here, it returns an empty string because by
        default the plugin has none.

        Note: CMOR has problems with None values. Instead the function returns
        an empty string.

        :return: Empty string
        :rtype: str
        """
        return 'none'
