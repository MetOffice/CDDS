# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`base_plugin` module contains the basic code for plugins.
"""
from abc import ABC
from enum import Enum
from cdds.common.plugins.plugins import CddsPlugin


class MipEra(Enum):
    """
    MIP eras of projects (e.g. cmip6, cmip7, ...)

    At the moment, only cmip6 is supported. That will change
    in the near future.
    """

    @staticmethod
    def from_str(str_value: str) -> 'MipEra':
        """
        Returns the corresponding MIP era to the given string representation.

        :param str_value: MIP era as string
        :type str_value: str
        :return: MIP era
        :rtype: MipEra
        """
        for mip_era in MipEra:
            if mip_era.value == str_value:
                return mip_era
        raise ValueError("Cannot find MIP era for {}".format(mip_era))

    @staticmethod
    def is_cmip(mip_era: str) -> bool:
        """
        Checks if given project is a CMIP project.

        :param mip_era: ID of project to check (case-sensitive check!)
        :type mip_era: str
        :return: True if project is a CMIP project otherwise False
        :rtype: bool
        """
        for cmip_era in [MipEra.CMIP6]:
            if mip_era == cmip_era.value:
                return True
        return False

    @staticmethod
    def is_gcmodeldev(mip_era: str) -> bool:
        """
        Checks if given project is a GcModelDev project.

        :param mip_era: ID of project to check (case-sensitive check!)
        :type mip_era: str
        :return: True if project is a GcModelDev project otherwise False
        :rtype: bool
        """
        for cmip_era in [MipEra.GC_MODEL_DEV]:
            if mip_era == cmip_era.value:
                return True
        return False

    CMIP6 = "CMIP6"
    GC_MODEL_DEV = "GCModelDev"


class BasePlugin(CddsPlugin, ABC):
    """
    Abstract class that provides some basic functionality for plugins.
    """

    def __init__(self, mip_era: MipEra):
        super(BasePlugin, self).__init__(mip_era.value)
