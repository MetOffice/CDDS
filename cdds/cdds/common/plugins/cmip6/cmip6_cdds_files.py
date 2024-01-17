# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cmip6_cdds_files` module contains the code required
to handle the paths to the CDDS specific directories and files.
"""
import os

from cdds.common.plugins.base.base_cdds_files import BaseCddsPaths


class Cmip6CddsPaths(BaseCddsPaths):
    """
    Provides functionalities to get the paths to the CDDS specific
    directories and files.
    """

    def mip_table_dir(self) -> str:
        """
        Returns the path to the MIP table directory that should be used for CMIP6

        :return: Path to the MIP table directory
        :rtype: str
        """
        return '{}/mip_tables/CMIP6/01.00.29/'.format(os.environ['CDDS_ETC'])
