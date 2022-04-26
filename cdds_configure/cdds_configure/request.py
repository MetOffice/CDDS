# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`request` module contains the code required to manipulate the
information about the request.
"""
from collections import OrderedDict, defaultdict
from copy import copy
import logging

from hadsdk.constants import USER_CONFIG_OPTIONS

from cdds_configure.constants import TEMPLATE_OPTIONS


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


def retrieve_required_keys(template, ignore_keys=[]):
    """
    Return the keys that must exist in the JSON file containing the
    information from the request for CDDS Configure.

    Parameters
    ----------
    template: bool
        Whether to create template |user configuration files|.
    ignore_keys: list (optional)
        The keys that should be ignored for the requirement check.

    Returns
    -------
    : list
        The keys that must exist in the JSON file containing the
        information from the request for CDDS Configure.
    """
    # Note that `hadsdk.read_request` handles the required keys related
    # to accessing the general configuration file.
    required_keys = sorted(required_keys_for_request())

    # Remove keys if the 'template' argument is provided.
    if template:
        required_keys = [
            key for key in required_keys if key not in list(TEMPLATE_OPTIONS.keys())]

    # Remove keys if a default argument exists.
    for key in ignore_keys:
        if key in required_keys:
            required_keys.remove(key)

    return required_keys


def validate_branch_options(request):
    """
    Validate the branch options.

    If the ``branch_method`` in the information about the request has a
    value that is not ``no parent``, the information about the request
    is validated to ensure that it contains all the required branch
    options.

    Parameters
    ----------
    request: :class:`hadsdk.request.Request`
        The information about the request.
    """
    required_branch_options = []
    if request.branch_method != 'no parent':
        for options in list(USER_CONFIG_OPTIONS.values()):
            if 'branch' in options:
                required_branch_options.extend(options['branch'])
    request.validate(required_branch_options)


def retrieve_request_metadata(request, template):
    """
    Return the metadata common to all |user configuration files|.

    The metadata common to all |user configuration files| are returned
    as a nested dictionary that can be written to a file via
    :mod:`configparser`, e.g. ``{section1: {option1: value1, option2:
    value2}, {section2: {}}``.

    Parameters
    ----------
    request: :class:`hadsdk.request.Request`
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
        if request.branch_method != 'no parent':
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
        value = getattr(request, option, None)
    return value


def _add_items(config, section, option, value):
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    logger.debug('Adding option "{}" to section "{}" with value "{}"'
                 ''.format(option, section, value))
    config[section][option] = value
