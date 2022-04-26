# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`user_config` module contains the code required to produce the
|user configuration files|.
"""
from collections import OrderedDict
from copy import deepcopy
import logging
import os

from hadsdk.configuration.python_config import PythonConfig
from hadsdk.request import read_request
from hadsdk.variables import RequestedVariablesList

from cdds_common.cdds_plugins.plugins import PluginStore

from cdds_configure import __version__
from cdds_configure.constants import HEADER_TEMPLATE
from cdds_configure.request import retrieve_required_keys, validate_branch_options, retrieve_request_metadata
from cdds_configure.variables import retrieve_variables_by_grid


def produce_user_config_files(arguments):
    """
    Produce the |user configuration files|.

    Parameters
    ----------
    arguments: :class:`cdds_configure.hadsdk.arguments.ConfigureArguments`
        The arguments specific to the `cdds_configure` script.
    """
    # Read and validate the information from the request.
    request = read_and_validate_request(arguments.request, arguments.args, arguments.template)

    create_user_config_files(request, arguments.requested_variables_list_file, arguments.user_config_template_name,
                             arguments.output_dir, arguments.template)


def read_and_validate_request(request_path, default_request_items, template=True):
    """
    Read and validate the information from the request for producing the |user configuration files|.

    Parameters
    ----------
    request_path: str
        The full path to the JSON file containing the information from the request.
    default_request_items: dict
        The default items to be added to the request.
    template: bool (optional)
        Whether to create template |user configuration files|. Default: True.

    Returns
    -------
    : :class:`hadsdk.request.Request`
        The information from the request.
    """
    required_keys = retrieve_required_keys(template, default_request_items.keys())
    request = read_request(request_path, required_keys, default_request_items)
    validate_branch_options(request)
    return request


def create_user_config_files(request, requested_variables_file, template_name, output_dir=None, template=True):
    """
    Creates the |user configuration files|.

    Parameters
    ----------
    request: :class:`hadsdk.request.Request`
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

    # Ensure the information from the request and the information from the 'requested variables list' are consistent.
    validate_request_with_requested_variables_list(request, requested_variables_list)

    # Determine the contents of the 'user configuration file'.
    user_configs = produce_user_configs(request, requested_variables_list, template, template_name)

    # Write 'user configuration file'.
    header = HEADER_TEMPLATE.format(__version__)

    for filename, user_config in user_configs.items():
        if output_dir is not None:
            filename = os.path.join(output_dir, filename)
        logger.info("Write configuration to: {}".format(filename))
        PythonConfig(user_config).write(filename, header=header)


def produce_user_configs(request, requested_variables_list, template,
                         template_name):
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
    request: :class:`hadsdk.request.Request`
        The information from the request.
    requested_variables_list: :class:`hadsdk.variables.RequestedVariablesList`
        The information from the |requested variables list|.
    template: bool
        Whether to create template |user configuration files|.
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
    metadata = retrieve_request_metadata(request, template)

    # Retrieve 'MIP requested variables' by grid.
    variables_by_grid = retrieve_variables_by_grid(requested_variables_list)

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
            user_config = OrderedDict()
            user_config.update(deepcopy(metadata))
            user_config['cmor_dataset']['grid'] = grid
            user_config['cmor_dataset']['grid_label'] = grid_label
            user_config['cmor_dataset']['nominal_resolution'] = nominal_resolution
            user_config['global_attributes'] = get_global_attributes(request)
            user_config.update(mip_requested_variables)
            filename = template_name.format(file_suffix)
            user_configs[filename] = user_config

    return user_configs


def get_global_attributes(request):
    """
    Returns all global attributes for the user configuration based on the
    given request values.

    :param request: Request contains all data to create the global attributes
    :type request: :class:`hadsdk.request.Request`
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
    :type request: :class:`hadsdk.request.Request`
    :return: Further info url
    :rtype: str
    """
    plugin = PluginStore.instance().get_plugin()
    global_attributes = plugin.global_attributes(request.items)
    return global_attributes.further_info_url()


def validate_request_with_requested_variables_list(request,
                                                   requested_variables_list):
    """
    Ensure the information from the request is consistent with the
    information from the requested variables.

    Parameters
    ----------
    request: :class:`hadsdk.request.Request`
        The information from the request.
    requested_variables_list: :class:`hadsdk.variables.RequestedVariablesList`
        The information from the |requested variables list|.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    common_keys = set(request.ALLOWED_ATTRIBUTES).intersection(
        set(requested_variables_list.ALLOWED_ATTRIBUTES))

    for key in common_keys:
        request_value = getattr(request, key)
        rvl_value = getattr(requested_variables_list, key)
        if request_value == rvl_value:
            logger.debug(
                '"{}" is consistent between the request JSON file and the '
                'the requested variables list'.format(key))
        else:
            raise RuntimeError(
                '"{}" is not consistent between the request JSON file ({}) '
                'and the requested variables list ({})'.format(
                    key, request_value, rvl_value))
