# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`request` module contains the code required to manipulate the
information about the request.
"""
from collections import OrderedDict, defaultdict
from copy import copy
import logging
import metomi.isodatetime.dumpers as dump
from metomi.isodatetime.data import TimePoint
import os

from cdds.configure.constants import (TEMPLATE_OPTIONS, NETCDF_FILE_ACTION, CREATE_SUBDIRECTORIES, DEFLATE_LEVEL,
                                      SHUFFLE)
from cdds.common.constants import USER_CONFIG_OPTIONS, DATE_TIME_FORMAT
from cdds.common.request.request import Request
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.plugins import PluginStore


def retrieve_request_metadata(request: Request):
    ordered_metadata: OrderedDict[str, dict] = OrderedDict({'cmor_setup': {}, 'cmor_dataset': {}, 'request': {}})
    ordered_metadata['cmor_setup'].update({'mip_table_dir': request.common.mip_table_dir})
    for item in USER_CONFIG_OPTIONS['cmor_dataset']['required']:
        if item == 'output_dir':
            continue
        val = getattr(request.metadata, item)
        if type(val) is TimePoint:
            val = dump.TimePointDumper().strftime(val, DATE_TIME_FORMAT)
        ordered_metadata['cmor_dataset'].update({item: val})
    if request.metadata.branch_method not in ['', 'no parent']:
        for item in USER_CONFIG_OPTIONS['cmor_dataset']['branch']:
            val = getattr(request.metadata, item)
            if type(val) is TimePoint:
                val = dump.TimePointDumper().strftime(val, DATE_TIME_FORMAT)
            ordered_metadata['cmor_dataset'].update({item: val})
    ordered_metadata['request'].update(
        {'base_date': dump.TimePointDumper().strftime(request.metadata.base_date, DATE_TIME_FORMAT)})
    ordered_metadata['cmor_setup'].update({'cmor_log_file': '{{ cmor_log }}'})
    ordered_metadata['cmor_setup'].update({'netcdf_file_action': NETCDF_FILE_ACTION})
    ordered_metadata['cmor_setup'].update({'create_subdirectories': CREATE_SUBDIRECTORIES})

    ordered_metadata['cmor_dataset'].update({'output_dir': '{{ output_dir }}'})
    ordered_metadata['cmor_dataset'].update({'license': request.metadata.license})
    if request.metadata.experiment_id:
        ordered_metadata['cmor_dataset'].update({'experiment_id': request.metadata.experiment_id})
        ordered_metadata['cmor_dataset'].update({'sub_experiment_id': request.metadata.sub_experiment_id})

    ordered_metadata['request'].update({'model_output_dir': '{{ input_dir }}'})
    ordered_metadata['request'].update({'run_bounds': '{{ start_date }} {{ end_date }}'})
    ordered_metadata['request'].update({'suite_id':  request.data.model_workflow_id})
    ordered_metadata['request'].update({'ancil_files': get_ancil_files(request)})
    ordered_metadata['request'].update({'ancil_variables': get_ancil_variables(request)})
    ordered_metadata['request'].update({'hybrid_heights_files': get_hybrid_heights_files(request)})
    ordered_metadata['request'].update({'replacement_coordinates_file': get_replacement_coordinates_file(request)})
    ordered_metadata['request'].update({'deflate_level': DEFLATE_LEVEL})
    ordered_metadata['request'].update({'sites_file': request.common.sites_file})
    ordered_metadata['request'].update({'shuffle': SHUFFLE})
    return ordered_metadata


def _get_value(request, option, template):
    get_value_from_request = False
    if template:
        if option in TEMPLATE_OPTIONS:
            value = '{{{{ {} }}}}'.format(
                ' }} {{ '.join(TEMPLATE_OPTIONS[option]))
        else:
            get_value_from_request = True
    else:
        get_value_from_request = True
    if get_value_from_request:
        value = request.items.get(option)
    return value


def _add_items(config, section, option, value):
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    logger.debug('Adding option "{}" to section "{}" with value "{}"'
                 ''.format(option, section, value))
    config[section][option] = value


def get_ancil_files(request):
    """
    Constructs the full paths to the ancillary files for a specific model
    and makes them available via the ``ancil_files`` and ``args`` attributes.
    """
    root_dir = request.common.root_ancil_dir

    plugin = PluginStore.instance().get_plugin()
    models_parameters = plugin.models_parameters(request.metadata.model_id)
    ancil_files = models_parameters.all_ancil_files(root_dir)
    return ' '.join(ancil_files)


def get_ancil_variables(request):
    """
    Returns all additional ancillary variables for a specific model
    """
    plugin = PluginStore.instance().get_plugin()
    models_parameters = plugin.models_parameters(request.metadata.model_id)
    ancil_variables = models_parameters.all_ancil_variables()
    return ' '.join(ancil_variables)


def get_replacement_coordinates_file(request):
    """
    Constructs the full paths to the replacement coordinates file for a specific
    model and makes them available via the ``replacement_coordinates_file`` and
    ``args`` attributes.
    """
    root_dir = request.common.root_replacement_coordinates_dir
    plugin = PluginStore.instance().get_plugin()
    grid_info = plugin.grid_info(request.metadata.model_id, GridType.OCEAN)
    filename = grid_info.replacement_coordinates_file
    return os.path.join(root_dir, filename) if filename else ''


def get_hybrid_heights_files(request):
    """
    Constructs the full paths to the hybrid heights files of a specific
    model and overwrites the hybrid_heights_files attribute.

    :param model_id: ID of model
    :type model_id: str
    """
    root_dir = request.common.root_hybrid_heights_dir
    plugin = PluginStore.instance().get_plugin()
    models_parameters = plugin.models_parameters(request.metadata.model_id)
    hybrid_heights_files = models_parameters.all_hybrid_heights_files(root_dir)
    return ' '.join(hybrid_heights_files)
