# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`gcmodeldev_cdds_files` module contains the code required
to handle the paths to the CDDS specific directories and files.
"""
import os

from cdds.common.plugins.base.base_cdds_files import BaseCddsPaths


class GCModelDevCddsPaths(BaseCddsPaths):
    """
    Provides functionalities to get the paths to the CDDS specific
    directories and files.
    """

    def mip_table_dir(self) -> str:
        """
        Returns the path to the MIP table directory that should be used for GCModelDev

        :return: Path to the MIP table directory
        :rtype: str
        """
        return '{}/mip_tables/GCModelDev/0.0.13'.format(os.environ['CDDS_ETC'])
