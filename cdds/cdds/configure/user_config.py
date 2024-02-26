# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`user_config` module contains the code required to produce the
|user configuration files|.
"""
from collections import OrderedDict
from copy import deepcopy
import logging
import os

from mip_convert.configuration.python_config import PythonConfig

from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.grid import GridType
from cdds.common.request.request import read_request
from cdds.common.variables import RequestedVariablesList

from cdds import __version__
from cdds.configure.constants import HEADER_TEMPLATE
from cdds.configure.request import retrieve_required_keys, validate_branch_options, retrieve_request_metadata
from cdds.configure.variables import retrieve_variables_by_grid, retrieve_streams_by_grid


def produce_user_config_files(arguments):
    """
    Produce the |user configuration files|.

    Parameters
    ----------
    arguments: :class:`cdds.configure.cdds.arguments.ConfigureArguments`
        The arguments specific to the `configure` script.
    """
    request = read_request(arguments.request)

    create_user_config_files(request, arguments.requested_variables_list_file, arguments.user_config_template_name,
                             arguments.output_dir, arguments)


def create_user_config_files(request, requested_variables_file, template_name, output_dir=None, args=None):
    """
    Creates the |user configuration files|.

    Parameters
    ----------
    request: :class:`cdds.common.old_request.Request`
        The information from the request.
    requested_variables_file: str
        The full path to the |requested variables list|.
    template_name: str
        The template for the name of the |user configuration files|.
    output_dir: str (optional)
        The full path to the directory where the |user configuration files| will be written.
    template: bool (optional)
        Whether to create template |user configuration files|. Default: True.
    """
    logger = logging.getLogger(__name__)
    # Read and validate the information from the 'requested variables list'.
    requested_variables_list = RequestedVariablesList(requested_variables_file)

    # Determine the contents of the 'user configuration file'.
    user_configs = produce_user_configs(request, requested_variables_list, template_name, args)

    # Write 'user configuration file'.
    header = HEADER_TEMPLATE.format(__version__)

    for filename, user_config in user_configs.items():
        if output_dir is not None:
            filename = os.path.join(output_dir, filename)
        logger.info("Write configuration to: {}".format(filename))
        PythonConfig(user_config).write(filename, header=header)


def produce_user_configs(request, requested_variables_list, template_name, args):
    """
    Return the contents of the |user configuration files|.

    The contents of the |user configuration files| are returned as a
    dictionary in the form ``{filename1: {user_config1}, filename2:
    {user_config2}``, where the key is the name of the
    |user configuration file| and the value is a nested dictionary that
    can be written to a file via :mod:`configparser`, e.g. ``{section1:
    {option1: value1, option2: value2}, section2: {}}``.

    Parameters
    ----------
    request: :class:`cdds.common.old_request.Request`
        The information from the request.
    requested_variables_list: :class:`cdds.common.variables.RequestedVariablesList`
        The information from the |requested variables list|.
    template_name: string
        The template for the name of the |user configuration files|.

    Returns
    -------
    : dict
        The contents of the |user configuration files|.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Retrieve metadata common to all 'user configuration files'.
    metadata = retrieve_request_metadata(request, args)

    # Retrieve 'MIP requested variables' by grid.
    variables_by_grid = retrieve_variables_by_grid(requested_variables_list, request.mip_table_dir)
    streams = retrieve_streams_by_grid(requested_variables_list)

    # Produce the contents of the 'user configuration files' by grid.
    user_configs = OrderedDict()
    for grid_info, mip_requested_variables in variables_by_grid.items():
        grid_id, grid, grid_label, nominal_resolution, substream = grid_info
        if mip_requested_variables:
            if substream is None:
                file_suffix = grid_id
            else:
                file_suffix = '{}-{}'.format(grid_id, substream)
            logger.info(
                'Producing user configuration file for "{}"'.format(file_suffix))
            maskings = get_masking_attributes(request.metadata.model_id, streams)
            user_config = OrderedDict()
            user_config.update(deepcopy(metadata))
            user_config['cmor_dataset']['grid'] = grid
            user_config['cmor_dataset']['grid_label'] = grid_label
            user_config['cmor_dataset']['nominal_resolution'] = nominal_resolution
            user_config['global_attributes'] = get_global_attributes(request)
            if maskings:
                user_config['masking'] = maskings
            user_config.update(mip_requested_variables)
            filename = template_name.format(file_suffix)
            user_configs[filename] = user_config
    return user_configs


def get_masking_attributes(model_id, streams):
    """
    Returns the masking for the ocean grid of given model. Only masks for the
    given streams are loaded.

    The key of the resulted dictionary composed of the prefix stream and the
    stream name and grid:
    'stream_<stream_name>_<grid>'
    If the grid is not given, the masking is valid for all grids of the stream.

    The value is the slices of latitude and longitude as string representation:
    '<lat_start>:<lat_stop>:<lat_step>,<lon_start>:<lon_stop>:<lon:step>'

    :param model_id: Model id
    :type model_id: str
    :param streams: Streams that masking is used
    :type streams: List[str]
    :return: A dictionary contains the masks according the stream and grid
    :rtype: OrderedDict[str, str]
    """
    maskings = OrderedDict()
    plugin = PluginStore.instance().get_plugin()
    grid_info = plugin.grid_info(model_id, GridType.OCEAN)
    masking_key_template = 'stream_{}_{}'
    masks = grid_info.masks
    for stream in streams:
        if masks:
            for grid, value in masks.items():
                key = masking_key_template.format(stream, grid)
                maskings[key] = value
    return maskings


def get_global_attributes(request):
    """
    Returns all global attributes for the user configuration based on the
    given request values.

    :param request: Request contains all data to create the global attributes
    :type request: :class:`cdds.common.old_request.Request`
    :return: Global attributes as dictionary
    :rtype: dict
    """
    global_attributes = OrderedDict()
    global_attributes['further_info_url'] = get_further_info_url(request)
    if request.items_global_attributes:
        global_attributes.update(request.items_global_attributes)
    return global_attributes


def get_further_info_url(request):
    """
    Returns the further info url according the request values.

    :param request: Request containing all values to create the further info url
    :type request: :class:`cdds.common.old_request.Request`
    :return: Further info url
    :rtype: str
    """
    plugin = PluginStore.instance().get_plugin()
    global_attributes = plugin.global_attributes(request.items)
    return global_attributes.further_info_url()
