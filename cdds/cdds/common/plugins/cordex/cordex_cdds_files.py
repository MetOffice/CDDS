# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cordex_cdds_files` module contains the code required
to handle the paths to the CDDS specific directories and files.
"""
import os

from cdds.common.plugins.base.base_cdds_files import BaseCddsPaths


class CordexCddsPaths(BaseCddsPaths):
    """
    Provides functionalities to get the paths to the CDDS specific
    directories and files.
    """

    def mip_table_dir(self) -> str:
        """
        Returns the path to the MIP table directory that should be used for CORDEX

        :return: Path to the MIP table directory
        :rtype: str
        """
        return '{}/mip_tables/CORDEX/for_functional_tests'.format(os.environ['CDDS_ETC'])
