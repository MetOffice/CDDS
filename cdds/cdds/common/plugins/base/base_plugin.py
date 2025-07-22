# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`base_plugin` module contains the basic code for plugins.
"""
import os

from abc import ABC
from enum import Enum
from typing import TYPE_CHECKING

from cdds.common.plugins.plugins import CddsPlugin

# Only used for type hints: There would be a package cycle otherwise
if TYPE_CHECKING:
    from cdds.common.request.request import Request


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
    def is_cmip_plus(mip_era: str) -> bool:
        """
        Checks if given project is a CMIPPlus project.

        :param mip_era: ID of project to check (case-sensitive check!)
        :type mip_era: str
        :return: True if project is a CMIPPlus project otherwise False
        :rtype: bool
        """
        for cmip_plus_era in [MipEra.CMIP6_Plus]:
            if mip_era == cmip_plus_era.value:
                return True
        return False

    @staticmethod
    def is_cmip7(mip_era: str) -> bool:
        """
        Checks if given project is a CMIP7 project.

        :param mip_era: ID of project to check (case-sensitive check!)
        :type mip_era: str
        :return: True if project is a CMIP7 project otherwise False
        :rtype: bool
        """
        for cmip_plus_era in [MipEra.CMIP7]:
            if mip_era == cmip_plus_era.value:
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

    @staticmethod
    def is_cordex(mip_era: str) -> bool:
        for cordex in [MipEra.CORDEX]:
            if mip_era == cordex.value:
                return True
        return False

    CMIP6 = "CMIP6"
    CMIP6_Plus = "CMIP6Plus"
    CMIP7 = "CMIP7"
    GC_MODEL_DEV = "GCModelDev"
    CORDEX = "CORDEX"


class BasePlugin(CddsPlugin, ABC):
    """
    Abstract class that provides some basic functionality for plugins.
    """

    def __init__(self, mip_era: str):
        super(BasePlugin, self).__init__(mip_era)

    def proc_directory(self, request: 'Request') -> str:
        """
        Returns the CDDS proc directory where the non-data ouputs are written.

        :param request: Information that is needed to define the proc directory
        :type request: Request
        :return: Path to the proc directory
        :rtype: str
        """
        return os.path.join(
            request.common.root_proc_dir,
            request.metadata.mip_era,
            request.metadata.mip,
            request.common.workflow_basename,
            request.common.package
        )

    def data_directory(self, request: 'Request') -> str:
        """
        Returns the CDDS data directory where the |model output files| are written.

        :param request: Information that is needed to define the data directory
        :type request: Request
        :return: Path to the data directory
        :rtype: str
        """
        return os.path.join(
            request.common.root_data_dir,
            request.metadata.mip_era,
            request.metadata.mip,
            request.metadata.model_id,
            request.metadata.experiment_id,
            request.metadata.variant_label,
            request.common.package
        )

    def requested_variables_list_filename(self, request: 'Request') -> str:
        """
        Returns the file name of the |requested variables list| file.

        :param request: Information that is needed to define the file name of the |requested variables list|
        :type request: Request
        :return: File name of the |requested variables list| file
        :rtype: str
        """
        name = '_'.join([
            request.metadata.mip_era,
            request.metadata.mip,
            request.metadata.experiment_id,
            request.metadata.model_id
        ])
        return '{}.json'.format(name)
