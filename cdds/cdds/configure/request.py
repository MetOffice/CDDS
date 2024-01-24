# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`request` module contains the code required to manipulate the
information about the request.
"""
from collections import OrderedDict, defaultdict
from copy import copy
import logging
import metomi.isodatetime.dumpers as dump
from metomi.isodatetime.data import TimePoint

from cdds.configure.constants import TEMPLATE_OPTIONS
from cdds.common.constants import USER_CONFIG_OPTIONS, DATE_TIME_FORMAT
from cdds.common.request.request import Request


def retrieve_request_metadata(request: Request, args):
    ordered_metadata = OrderedDict({'cmor_setup': {}, 'cmor_dataset': {}, 'request': {}})
    ordered_metadata['cmor_setup'].update({'mip_table_dir': request.common.mip_table_dir})
    for item in USER_CONFIG_OPTIONS['cmor_dataset']['required']:
        if item == 'output_dir':
            continue
        val = getattr(request.metadata, item)
        if type(val) is TimePoint:
            val = dump.TimePointDumper().strftime(val, DATE_TIME_FORMAT)
        ordered_metadata['cmor_dataset'].update({item: val})
    if request.metadata.branch_method != '':
        for item in USER_CONFIG_OPTIONS['cmor_dataset']['branch']:
            val = getattr(request.metadata, item)
            if type(val) is TimePoint:
                val = dump.TimePointDumper().strftime(val, DATE_TIME_FORMAT)
            ordered_metadata['cmor_dataset'].update({item: val})
        ordered_metadata['request'].update(
            {'child_base_date': dump.TimePointDumper().strftime(request.metadata.child_base_date, DATE_TIME_FORMAT)})
    ordered_metadata['cmor_setup'].update({'cmor_log_file': '{{ cmor_log }}'})
    ordered_metadata['cmor_dataset'].update({'output_dir': '{{ output_dir }}'})
    ordered_metadata['request'].update({'model_output_dir': '{{ input_dir }}'})
    ordered_metadata['request'].update({'run_bounds': '{{ start_date }} {{ end_date }}'})
    ordered_metadata['request'].update({'suite_id':  request.data.model_workflow_id})
    for section, items in USER_CONFIG_OPTIONS.items():
        for option_type, options in items.items():
            if option_type == 'optional':
                for option in options:
                    if option in args.args:
                        val = args.args[option]
                        if type(val) is TimePoint:
                            val = dump.TimePointDumper().strftime(val, DATE_TIME_FORMAT)
                        ordered_metadata[section].update({option: val})

    return ordered_metadata


def required_keys_for_request():
    """
    Return the required keys for a request.

    Returns
    -------
    : list
        List of required keys.
    """
    return [opt for opt_info in list(USER_CONFIG_OPTIONS.values())
            for opt_type, opts in opt_info.items()
            for opt in opts if opt_type == 'required']


def _retrieve_request_metadata(request, template):
    """
    Return the metadata common to all |user configuration files|.

    The metadata common to all |user configuration files| are returned
    as a nested dictionary that can be written to a file via
    :mod:`configparser`, e.g. ``{section1: {option1: value1, option2:
    value2}, {section2: {}}``.

    Parameters
    ----------
    request: :class:`cdds.common.old_request.Request`
        The information about the request.
    template: bool
        Whether to create template |user configuration files|.

    Returns
    -------
    : dict
        The metadata common to all |user configuration files|.
    """
    metadata = defaultdict(dict)
    for section, options in USER_CONFIG_OPTIONS.items():
        # Required options.
        required_options = copy(options['required'])
        if request.metadata.branch_method != 'no parent':
            if 'branch' in options:
                required_options.extend(options['branch'])
        for option in required_options:
            value = _get_value(request, option, template)
            if value is None:  # Shouldn't happen if required_keys is correct.
                raise AttributeError(
                    'Request must contain "{}"'.format(option))
            _add_items(metadata, section, option, value)
        # Optional options.
        optional_options = options['optional']
        for option in optional_options:
            value = _get_value(request, option, template)
            if value is not None:
                _add_items(metadata, section, option, value)

    # Order metadata.
    ordered_metadata = OrderedDict()
    for section in ['cmor_setup', 'cmor_dataset', 'request', 'global_attributes']:
        items = OrderedDict(sorted(metadata[section].items()))
        ordered_metadata[section] = items

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
