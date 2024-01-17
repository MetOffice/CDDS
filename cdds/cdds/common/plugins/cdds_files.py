# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`base_cdds_files` module contains the code required
to handle the paths to the CDDS specific directories and files.
"""
from abc import abstractmethod, ABCMeta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cdds.common.request.request import Request


class CddsPaths(object, metaclass=ABCMeta):
    """
    Provides functionalities to get the paths to the CDDS specific
    directories and files.
    """

    @abstractmethod
    def mip_table_dir(self) -> str:
        """
        Returns the path to the MIP table directory that should be used for project

        :return: Path to the MIP table directory
        :rtype: str
        """
        pass

    @abstractmethod
    def proc_directory(self, request: 'Request') -> str:
        """
        Returns the CDDS proc directory where the non-data ouputs are written.

        :param request: Information that is needed to define the proc directory
        :type request: Request
        :return: Path to the proc directory
        :rtype: str
        """
        pass

    @abstractmethod
    def data_directory(self, request: 'Request') -> str:
        """
        Returns the CDDS data directory where the |model output files| are written.

        :param request: Information that is needed to define the data directory
        :type request: Request
        :return: Path to the data directory
        :rtype: str
        """
        pass

    @abstractmethod
    def requested_variables_list_filename(self, request: 'Request') -> str:
        """
        Returns the file name of the |requested variables list| file.

        :param request: Information that is needed to define the file name of the |requested variables list|
        :type request: Request
        :return: File name of the |requested variables list| file
        :rtype: str
        """
        pass

    @abstractmethod
    def component_directory(self, request: 'Request', component: str) -> str:
        """
        Returns the specific component directory in the CDDS proc directory.

        :param request: Request containing all information about the proc directory
        :type request: Request
        :param component: Component
        :type component: str
        :return: Path to the specific component directory in the proc directory
        :rtype: str
        """
        pass

    @abstractmethod
    def log_directory(self, request: 'Request', component: str, create_if_not_exist: bool = False) -> str:
        """
        Return the full path to the directory where the log files for the CDDS component ``component`` are written
        within the proc directory or output dir if chosen.
        If the log directory does not exist, it will be created.
        If no log directory can be found it returns None.

        :param request: Request containing information about the CDDS directories
        :type request: Request
        :param component: The name of the CDDS component.
        :type component: str
        :param create_if_not_exist: Creates the log directory if not exists
        :type bool
        :return: The full path to the directory where the log files for the CDDS component are written within the
            proc directory. If no log directory can be found, None will be returned.
        :rtype: str
        """
        pass
