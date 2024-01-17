# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`base_cdds_files` module contains the code required
to handle the paths to the CDDS specific directories and files.
"""
import os

from abc import ABC
from typing import TYPE_CHECKING

from cdds.common.plugins.cdds_files import CddsPaths

if TYPE_CHECKING:
    from cdds.common.request.request import Request


LOG_DIRECTORY = 'log'


class BaseCddsPaths(CddsPaths, ABC):
    """
    Provides functionalities to get the paths to the CDDS specific
    directories and files.
    """

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
        if request.misc.use_proc_dir:
            proc_dir = self.proc_directory(request)
            return os.path.join(proc_dir, component)
        return None

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
        component_proc_dir = self.component_directory(request, component)

        if component_proc_dir is None:
            return None

        log_dir = os.path.join(component_proc_dir, LOG_DIRECTORY)
        if create_if_not_exist and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir
