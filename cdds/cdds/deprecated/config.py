# (C) British Crown Copyright 2018-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`config` module contains the code required to access the
``config`` for CDDS.
"""
import os

from configparser import NoSectionError, NoOptionError
from typing import Dict

from cdds.common.constants import (
    DATA_DIR_FACET_STRING, INPUT_DATA_DIRECTORY, LOG_DIRECTORY,
    OUTPUT_DATA_DIRECTORY, PROC_DIRECTORY_FACET_STRING,
    REQUESTED_VARIABLES_LIST_FACET_STRING)
from cdds.common import construct_string_from_facet_string
from cdds.common.request.request import Request
from mip_convert.configuration.python_config import PythonConfig


def load_override_values(read_path):
    """
    Return the override values from the configuration file.

    The override values are returned as a dictionary in the form
    ``{mip_table1: {var_name1: override_value1, var_name2:
    override_value2}, mip_table2: {}}``.

    Parameters
    ----------
    read_path: str
        The full path to the configuration file containing the
        override values.

    Returns
    -------
    : dict
        The override values.
    """
    # Read and validate the configuration file.
    config = PythonConfig(read_path)

    return {mip_table: config.items(mip_table)
            for mip_table in config.sections}


def update_arguments_paths(arguments, additional_paths_ids=[]):
    """
    Update all paths attributes specified in global_path_ids with
    their full qualified counterpart. Additional paths attributes
    can specified in additional_paths_ids.

    Parameters
    ----------
    arguments: :class:`cdds.arguments.Arguments`
        arguments object that contains paths that should be updated
    additional_paths_ids: list of path ids (optional)
        ids of path attributes that should be updated, too

    Returns
    -------
    : :class:`cdds.arguments.Arguments`
        arguments object that contains updated paths
    """
    global_path_ids = [
        'data_request_base_dir',
        'root_data_dir',
        'root_mip_table_dir',
        'standard_names_dir',
        'root_proc_dir',
        'output_dir',
        'root_config',
        'request'
    ]
    all_path_ids = global_path_ids + additional_paths_ids

    for path_id in all_path_ids:
        has_attribute = hasattr(arguments, path_id) and getattr(arguments, path_id) is not None
        if has_attribute:
            absolute_path = os.path.abspath(getattr(arguments, path_id))
            setattr(arguments, path_id, absolute_path)
    return arguments


def update_arguments_for_proc_dir(arguments, request, component):
    """
    Return the arguments as provided to the ``arguments`` parameter
    with the values updated to use the proc directory.

    Parameters
    ----------
    arguments: :class:`cdds.arguments.Arguments`
        The arguments.
    request: :class:`cdds.deprecate.config.Request`
        The information from the request.
    component: str
        The name of the CDDS component.

    Returns
    -------
    : :class:`cdds.arguments.Arguments`
        The arguments updated to use the proc directory.
    """
    # Determine the full paths to any inputs.
    full_paths = FullPaths(arguments, request)
    if hasattr(arguments, 'requested_variables_list_file'):
        arguments.requested_variables_list_file = (
            full_paths.requested_variables_list_file)

    # Determine the full paths to the outputs.
    arguments.output_dir = full_paths.component_directory(component)
    return arguments


def update_log_dir(arguments, component):
    """
    DEPRECATED: Moved to cdds.common.cdds_directories.log_directory
    Return the argumentas as provided to the ``arguments`` parameter
    with the updated log_name value that uses the full path to the
    log file if a specific log directory of the component can be
    found.

    Parameters
    ----------
    arguments: class:`cdds.arguments.Arguments`
        The arguments
    component: str
        The name of the CDDS component

    Returns
    -------
     : :class:`cdds.arguments.Arguments`
        The arguments updated to the full path of the log file if a log
        directory can be found.
    """
    full_paths = FullPaths(arguments, None)
    log_name = arguments.log_name
    log_dir = full_paths.log_directory(component)
    if log_dir is not None:
        arguments.log_name = os.path.join(log_dir, log_name)
    return arguments


class FullPaths(object):
    """
    TODO: deprecated Now provided by the new request object
    Store information about the full paths used by CDDS.
    """

    def __init__(self, arguments, request):
        """
        Construct the full paths using the arguments and the information
        from the request. See also
        :func:`cdds.common.construct_string_from_facet_string`.

        Parameters
        ----------
        arguments: :class:`cdds.arguments.Arguments` object
            The arguments.
        request: :class:`cdds.deprecate.config.Request`
            The information from the request.
        """
        self.arguments = arguments
        self.request = request

    @property
    def data_directory(self):
        """
        str: The root path to the directory where the |model output files|
             are written.
        """
        facet_string_path = construct_string_from_facet_string(
            DATA_DIR_FACET_STRING, self.request.items_for_facet_string)
        return os.path.join(self.arguments.root_data_dir, facet_string_path)

    @property
    def input_data_directory(self):
        """
        str: The full path to the directory where the |model output files|
             used as input to CDDS Convert are written.
        """
        return os.path.join(self.data_directory, INPUT_DATA_DIRECTORY)

    @property
    def output_data_directory(self):
        """
        str: The full path to the directory where the |output netCDF files|
             produced by CDDS Convert are written.
        """
        return os.path.join(self.data_directory, OUTPUT_DATA_DIRECTORY)

    @property
    def proc_directory(self):
        """
        str: The root path to the directory where the non-data outputs
        from each CDDS component are written.
        """
        facet_string_path = construct_string_from_facet_string(
            PROC_DIRECTORY_FACET_STRING, self.request.items_for_facet_string)
        return os.path.join(self.arguments.root_proc_dir, facet_string_path)

    @property
    def mip_table_dir(self):
        """
        str: The root path to the mip tables.
        """
        if hasattr(self.request, 'mip_table_dir'):
            return self.request.mip_table_dir
        else:
            return self.arguments.root_mip_table_dir

    def component_directory(self, component):
        """
        Return the full path to the component-specific directory within
        the proc directory.

        Parameters
        ----------
        component: str
            The name of the CDDS component.

        Returns
        -------
        : str
            The full path to the component-specific directory within the
            proc directory.
        """
        return os.path.join(self.proc_directory, component)

    def component_log_directory(self, component):
        """
        Return the full path to the common log directory of a CDDS component.
        This is used for logging if no other log directory is defined.

        Parameters
        ----------
        component: str
            The name of the CDDS component.

        Returns
        -------
        : str
            The full path to the common log directory of a CDDS component.
        """
        return os.path.join(self.component_directory(component), LOG_DIRECTORY)

    def log_directory(self, component):
        """
        DEPRECATED: Moved to cdds.cdds_directories.common.log_directory
        Return the full path to the directory where the log files for
        the CDDS component ``component`` are written within the proc
        directory or output dir if chosen.
        If the log directory does not exist, it will be created.
        If no log directory can be found it returns None.

        Parameters
        ----------
        component: str
            The name of the CDDS component.

        Returns
        -------
        : None|str
            The full path to the directory where the log files for the
            CDDS component are written within the proc directory.
            If no log directory can be found, None will be returned.
        """
        base_output_dir = self._get_base_output_dir(component)

        if base_output_dir is None:
            return None

        log_dir = os.path.join(base_output_dir, LOG_DIRECTORY)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir

    def _get_base_output_dir(self, component):
        if hasattr(self.arguments, 'output_dir'):
            return self.arguments.output_dir
        elif hasattr(self.arguments, 'use_proc_dir') and self.arguments.use_proc_dir:
            return self.component_directory(component)
        return None

    @property
    def requested_variables_list_filename(self):
        """
        Return the filename of the |requested variables list|
        corresponding to the supplied request.

        Returns
        -------
        : str
            The filename of the |requested variables list|.
        """
        facet_string_filename = construct_string_from_facet_string(
            REQUESTED_VARIABLES_LIST_FACET_STRING,
            self.request.items_for_facet_string, string_type='filename')
        return '{}.json'.format(facet_string_filename)

    @property
    def requested_variables_list_file(self):
        """
        Return the full path to the |requested variables list|
        corresponding to the supplied request within the proc directory.

        Returns
        -------
        : str
            The full path to the |requested variables list| within the
            proc directory.
        """
        return os.path.join(self.component_directory('prepare'),
                            self.requested_variables_list_filename)


class CDDSConfigGeneral(PythonConfig):
    """
    Store information read from the general configuration file for CDDS.
    """

    def __init__(self, root_config_directory: str, request: Request) -> None:
        """
        The general configuration file is named ``<mip_era>.cfg`` and must be located in the directory
        ``/<root_config_directory>/<mip_era>/general/``.

        :param root_config_directory: The root path to the directory containing the CDDS configuration files.
        :type root_config_directory: str
        :param request: The request containing the required values to construct the paths
            to the data and proc directories
        :type request: Request
        """
        self._root_config_directory = root_config_directory
        self.request = request
        super(CDDSConfigGeneral, self).__init__(self._read_path)

    @property
    def _general_config_filename(self):
        return '{}.cfg'.format(self.request.metadata.mip_era)

    @property
    def _read_path(self):
        return os.path.join(
            self._root_config_directory, self.request.metadata.mip_era,
            'general',
            self._general_config_filename)

    def _value(self, section, option, ptype):
        try:
            value = self.value(section, option, ptype)
        except (NoSectionError, NoOptionError):
            value = None
        return value

    @property
    def transfer_facetmaps(self) -> Dict[str, str]:
        """
        Return the dictionary of facet maps used in CDDS Transfer.

        :return: Entries from the `transfer_facetmaps` section of the general config file.
        :rtype: Dict[str, str]
        """
        return self.items('transfer_facetmaps')
