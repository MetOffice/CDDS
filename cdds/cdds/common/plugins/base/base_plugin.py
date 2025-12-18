# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`base_plugin` module contains the basic code for plugins."""
import os

from abc import ABC
from enum import Enum
from typing import TYPE_CHECKING

from cdds.common.plugins.plugins import CddsPlugin

# Only used for type hints: There would be a package cycle otherwise
if TYPE_CHECKING:
    from cdds.common.request.request import Request


class MipEra(Enum):
    """MIP eras of projects (e.g. cmip6, cmip7, ...)

    At the moment, only cmip6 is supported. That will change
    in the near future.
    """

    @staticmethod
    def from_str(str_value: str) -> 'MipEra':
        """Returns the corresponding MIP era to the given string representation.

        Parameters
        ----------
        str_value : str
            MIP era as string

        Returns
        -------
        MipEra
            MIP era
        """
        for mip_era in MipEra:
            if mip_era.value == str_value:
                return mip_era
        raise ValueError("Cannot find MIP era for {}".format(mip_era))

    @staticmethod
    def is_cmip(mip_era: str) -> bool:
        """Checks if given project is a CMIP project.

        Parameters
        ----------
        mip_era : str
            ID of project to check (case-sensitive check!)

        Returns
        -------
        bool
            True if project is a CMIP project otherwise False
        """
        for cmip_era in [MipEra.CMIP6]:
            if mip_era == cmip_era.value:
                return True
        return False

    @staticmethod
    def is_cmip_plus(mip_era: str) -> bool:
        """Checks if given project is a CMIPPlus project.

        Parameters
        ----------
        mip_era : str
            ID of project to check (case-sensitive check!)

        Returns
        -------
        bool
            True if project is a CMIPPlus project otherwise False
        """
        for cmip_plus_era in [MipEra.CMIP6_Plus]:
            if mip_era == cmip_plus_era.value:
                return True
        return False

    @staticmethod
    def is_cmip7(mip_era: str) -> bool:
        """Checks if given project is a CMIP7 project.

        Parameters
        ----------
        mip_era : str
            ID of project to check (case-sensitive check!)

        Returns
        -------
        bool
            True if project is a CMIP7 project otherwise False
        """
        for cmip_plus_era in [MipEra.CMIP7]:
            if mip_era == cmip_plus_era.value:
                return True
        return False

    @staticmethod
    def is_gcmodeldev(mip_era: str) -> bool:
        """Checks if given project is a GcModelDev project.

        Parameters
        ----------
        mip_era : str
            ID of project to check (case-sensitive check!)

        Returns
        -------
        bool
            True if project is a GcModelDev project otherwise False
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
    """Abstract class that provides some basic functionality for plugins."""

    def __init__(self, mip_era: str):
        super(BasePlugin, self).__init__(mip_era)

    def proc_directory(self, request: 'Request') -> str:
        """Returns the CDDS proc directory where the non-data ouputs are written.

        Parameters
        ----------
        request : Request
            Information that is needed to define the proc directory

        Returns
        -------
        str
            Path to the proc directory
        """
        return os.path.join(
            request.common.root_proc_dir,
            request.metadata.mip_era,
            request.metadata.mip,
            self.request_id(request),
            request.common.package
        )

    def data_directory(self, request: 'Request') -> str:
        """Returns the CDDS data directory where the |model output files| are written.

        Parameters
        ----------
        request : Request
            Information that is needed to define the data directory

        Returns
        -------
        str
            Path to the data directory
        """
        return os.path.join(
            request.common.root_data_dir,
            request.metadata.mip_era,
            request.metadata.mip,
            self.request_id(request),
            request.common.package
        )

    def request_id(self, request: 'Request') -> str:
        """Return a concatenation of model_id, experiment_id, and variant_label to uniquely identify a simulation.

        Parameters
        ----------
        request : Request
            The users request.

        Returns
        -------
        str
            The unique request_id
        """
        return f"{request.metadata.model_id}_{request.metadata.experiment_id}_{request.metadata.variant_label}"

    def requested_variables_list_filename(self, request: 'Request') -> str:
        """Returns the file name of the |requested variables list| file.

        Parameters
        ----------
        request : Request
            Information that is needed to define the file name of the |requested variables list|

        Returns
        -------
        str
            File name of the |requested variables list| file
        """
        name = '_'.join([
            request.metadata.mip_era,
            request.metadata.mip,
            request.metadata.experiment_id,
            request.metadata.model_id
        ])
        return '{}.json'.format(name)
