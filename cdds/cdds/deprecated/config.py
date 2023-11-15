# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`config` module contains the code required to access the
``config`` for CDDS.
"""
import os

from configparser import NoSectionError, NoOptionError

from cdds.common.constants import (
    DATA_DIR_FACET_STRING, INPUT_DATA_DIRECTORY, LOG_DIRECTORY,
    OUTPUT_DATA_DIRECTORY, PROC_DIRECTORY_FACET_STRING,
    REQUESTED_VARIABLES_LIST_FACET_STRING)
from cdds.common import construct_string_from_facet_string
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


def use_proc_dir(arguments, request, component):
    """
    Return the arguments as provided to the ``arguments`` parameter
    with the values updated to use the proc directory.

    Parameters
    ----------
    arguments: :class:`argparse.Namespace` object
        The names of the command line arguments and their values.
    request: :class:`cdds.deprecate.config.Request`
        The information from the request.
    component: str
        The name of the CDDS component
    """
    # Read and validate the general configuration file.
    config_general = CDDSConfigGeneral(arguments.root_config, request)

    # Determine the full paths to any inputs.
    if hasattr(arguments, 'requested_variables_list_file'):
        arguments.requested_variables_list_file = (
            config_general.requested_variables_list_file)

    # Determine the full paths to the outputs.
    arguments.output_dir = config_general.component_directory(component)
    arguments.log_name = os.path.join(
        config_general.log_directory(component), arguments.log_name)

    return arguments


class CDDSConfigGeneral(PythonConfig):
    """
    Store information read from the general configuration file for CDDS.
    """

    def __init__(self, root_config_directory, request):
        """
        The general configuration file is named ``<mip_era>.cfg`` and
        must be located in the directory
        ``/<root_config_directory>/<mip_era>/<config_version>/general/``.

        Parameters
        ----------
        root_config_directory: str
            The root path to the directory containing the CDDS
            configuration files.
        request: :class:`cdds.common.request.Request`
            The items required to construct the full paths to the
            data and proc directories, see
            :func:`cdds.common.construct_string_from_facet_string`.
        """
        self._root_config_directory = root_config_directory
        self.request = request
        super(CDDSConfigGeneral, self).__init__(self._read_path)

    @property
    def _general_config_filename(self):
        return '{}.cfg'.format(self.request.mip_era)

    @property
    def _read_path(self):
        return os.path.join(
            self._root_config_directory, self.request.mip_era,
            'v{}'.format(self.request.config_version), 'general',
            self._general_config_filename)

    def _value(self, section, option, ptype):
        try:
            value = self.value(section, option, ptype)
        except (NoSectionError, NoOptionError):
            value = None
        return value

    @property
    def _root_data_directory(self):
        return self.value('locations', 'dataroot', str)

    @property
    def _root_proc_directory(self):
        return self.value('locations', 'procroot', str)

    @property
    def _root_ancil_directory(self):
        return self.value('locations', 'root_ancil_dir', str)

    @property
    def _mip_table_directory(self):
        return self.value('locations', 'mip_table_dir', str)

    @property
    def _data_request_directory(self):
        return self.value('locations', 'data_request_dir', str)

    @property
    def _standard_names_directory(self):
        return self.value('locations', 'standard_names_dir', str)

    @property
    def _controlled_vocabulary_directory(self):
        return self.value('locations', 'controlled_vocabulary_dir', str)

    @property
    def _data_directory_facet_string(self):
        return self.value('facetmaps', 'datamap', str)

    @property
    def _proc_directory_facet_string(self):
        return self.value('facetmaps', 'procmap', str)

    @property
    def _ancil_directory_facet_string(self):
        return self.value('facetmaps', 'ancilmap', str)

    @property
    def _requested_variables_list_facet_string(self):
        return self.value('facetmaps', 'varfilemap', str)

    @property
    def _data_request_version(self):
        return self.value('external_versions', 'data_request', str)

    @property
    def _data_request_version_for_model_setup(self):
        return self.value(
            'data_request_version_for_model_setup', self.request.model_id, str)

    @property
    def _cmor_version(self):
        return self.value('external_versions', 'CMOR', str)

    @property
    def _ancil_filenames(self):
        return sorted(self.items('ancillaries').values())

    @property
    def _hybrid_heights_files(self):
        return self._value('auxiliary_files', 'hybrid_heights_files', str)

    @property
    def _replacement_coordinates_file(self):
        return self._value('auxiliary_files', 'replacement_coordinates_file',
                           str)

    @property
    def _sites_file(self):
        return self._value('auxiliary_files', 'sites_file', str)

    @property
    def data_directory(self):
        """
        str: The root path to the directory where the
        |model output files| are written.
        """
        facet_string_path = construct_string_from_facet_string(
            self._data_directory_facet_string,
            self.request.items_for_facet_string)
        return os.path.join(self._root_data_directory, facet_string_path)

    @property
    def input_data_directory(self):
        """
        str: The full path to the directory where the
        |model output files| used as input to CDDS Convert are
        written.
        """
        return os.path.join(self.data_directory, INPUT_DATA_DIRECTORY)

    @property
    def output_data_directory(self):
        """
        str: The full path to the directory where the
        |output netCDF files| produced by CDDS Convert are written.
        """
        return os.path.join(self.data_directory, OUTPUT_DATA_DIRECTORY)

    @property
    def proc_directory(self):
        """
        str: The root path to the directory where the non-data outputs
        from each CDDS component are written.
        """
        facet_string_path = construct_string_from_facet_string(
            self._proc_directory_facet_string,
            self.request.items_for_facet_string)
        return os.path.join(self._root_proc_directory, facet_string_path)

    def component_directory(self, component):
        """
        Return the full path to the component-specific directory.

        Parameters
        ----------
        component: str
            The name of the CDDS component.

        Returns
        -------
        : str
            The full path to the component-specific directory.
        """
        return os.path.join(self.proc_directory, component)

    def log_directory(self, component):
        """
        Return the full path to the directory where the log files from
        each CDDS component are written.

        Parameters
        ----------
        component: str
            The name of the CDDS component.

        Returns
        -------
        : str
            The full path to the directory where the log files from
            each CDDS component are written.
        """
        return os.path.join(self.component_directory(component), LOG_DIRECTORY)

    @property
    def mip_table_dir(self):
        """
        Return the full path to the directory where the MIP tables are
        located.

        Returns
        -------
        : str
            The full path to the directory where the MIP tables are
            located.
        """
        return self._mip_table_directory

    @property
    def data_request_directory(self):
        """
        Return the full path to the directory where the checkout of the
        data request versions are located.

        Returns
        -------
        : str
            The full path to the directory where the MIP tables are
            located.
        """
        return self._data_request_directory

    @property
    def standard_names_directory(self):
        """
        Return the full path to the directory where the standard names table
        is located.

        Returns
        -------
        : str
            The full path to the directory where the standard names table is
            located.
        """
        return self._standard_names_directory

    @property
    def controlled_vocabulary_directory(self):
        """
        Return the full path to the directory where the CV files are
        located.

        Returns
        -------
        : str
            The full path to the directory where the CV files are
            located.
        """
        return self._controlled_vocabulary_directory

    @property
    def requested_variables_list_filename(self):
        """
        Return the filename of the |requested variables list|
        corresponding to the supplied request.

        Returns
        -------
        : str
            The filename of the |requested variables list|
        """
        facet_string_filename = construct_string_from_facet_string(
            self._requested_variables_list_facet_string,
            self.request.items_for_facet_string, string_type='filename')
        return '{}.json'.format(facet_string_filename)

    @property
    def requested_variables_list_file(self):
        """
        Return the full path to the |requested variables list|
        corresponding to the supplied request.

        Returns
        -------
        : str
            The full path to the |requested variables list|
        """
        return os.path.join(self.component_directory('prepare'),
                            self.requested_variables_list_filename)

    @property
    def data_request_version_for_model_setup(self):
        """
        Return the data request version used to configure the model
        corresponding to the supplied request.

        Returns
        -------
        : str
            The data request version used to configure the model.
        """
        return self._data_request_version_for_model_setup

    @property
    def data_request_version(self):
        """
        Return the data request version used for a given run of CDDS.

        Returns
        -------
        : str
            The data request version used for a given run of CDDS.
        """
        return self._data_request_version

    @property
    def cmor_version(self):
        """
        Return the CMOR version used for a given run of CDDS.

        Returns
        -------
        : str
            The CMOR version used for a given run of CDDS.
        """
        return self._cmor_version

    @property
    def ancil_files(self):
        """
        Return the full paths to the ancillary files.

        Returns
        -------
        : list of strings
            The full paths to the ancillary files.
        """
        facet_string_path = construct_string_from_facet_string(
            self._ancil_directory_facet_string,
            self.request.items_for_facet_string)
        ancil_dir = os.path.join(self._root_ancil_directory, facet_string_path)
        return ' '.join(os.path.join(ancil_dir, filename)
                        for filename in self._ancil_filenames)

    @property
    def hybrid_heights_files(self):
        """
        Return the full path to the hybrid heights files.

        Returns
        -------
        : str
            The full path to the hybrid heights files.
        """
        return self._hybrid_heights_files

    @property
    def replacement_coordinates_file(self):
        """
        Return the full path to the replacement coordinates file.

        Returns
        -------
        : str
            The full path to the replacement coordinates file.
        """
        return self._replacement_coordinates_file

    @property
    def sites_file(self):
        """
        Return the full path to the sites file.

        Returns
        -------
        : str
            The full path to the sites file.
        """
        return self._sites_file

    @property
    def transfer_facetmaps(self):
        """
        Return the dictionary of facet maps used in CDDS Transfer.

        Returns
        -------
        : dict
            Entries from the `transfer_facetmaps` section of
            the general config file.
        """
        return self.items('transfer_facetmaps')

    @property
    def transfer_mass_top_dir(self):
        """
        Return the top directory for storing data in MASS.

        Returns
        -------
        : str
            MOOSE URI of top directory in MASS.
        """
        return self.value('transfer_mass', 'top_dir', str)

    @property
    def transfer_local_base_dir(self):
        """
        Return the "base_dir" for CDDS Transfer. This is the name of
        the directory between the data directory and the directory
        structure holding the files produced by CDDS Convert.

        Returns
        -------
        : str
            Name of the base directory.
        """
        return self.value('transfer_local', 'base_dir', str)

    @property
    def reference_time(self):
        return self.request.reference_time
