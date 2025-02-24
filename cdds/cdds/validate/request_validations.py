# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module providing functionality to validate request configuration
"""
import logging

from configparser import ConfigParser
from metomi.isodatetime.data import Calendar
from typing import Tuple, List

from cdds.common.request.request import load_cdds_plugins
from cdds.common.request.request import Request
from cdds.common.request.metadata_section import MetadataSection
from cdds.common.request.misc_section import MiscSection
from cdds.common.request.inventory_section import InventorySection
from cdds.common.request.common_section import CommonSection
from cdds.common.request.data_section import DataSection
from cdds.common.configparser.interpolation import EnvInterpolation
from cdds.common.request.request_validations import validate_request
from cdds.common.request.request_section import expand_path
from cdds.common.request.validations.exceptions import CVPathError, CVEntryError

from cdds.common.plugins.plugins import PluginStore


def do_request_validations(request_path: str) -> Tuple[bool, List[str]]:
    """
    Validates request stored at given path

    :param request_path: Path to the request to validate
    :type request_path: str
    :return: Is valid and a list of messages
    :rtype: Tuple[bool, List[str]]
    """
    logger = logging.getLogger(__name__)
    valid = True
    messages = []

    interpolation = EnvInterpolation()
    request_config = ConfigParser(interpolation=interpolation, inline_comment_prefixes=('#',))
    request_config.optionxform = str  # Preserve case.
    request_config.read(request_path)
    if request_config.has_section('inheritance'):
        template = request_config.get('inheritance', 'template')
        if template:
            template_path = expand_path(template)
            interpolation = EnvInterpolation()
            request_config = ConfigParser(interpolation=interpolation, inline_comment_prefixes=('#',))
            request_config.optionxform = str  # Preserve case.
            request_config.read([template_path, request_path])

    load_cdds_plugins(request_config)

    calendar = request_config.get('metadata', 'calendar')
    Calendar.default().set_mode(calendar)

    try:
        MetadataSection.from_config(request_config)
    except AttributeError as e:
        logger.error('Metadata section is invalid: {}'.format(e.args[0]))
        valid = False
        messages.append(e.args[0])

    try:
        CommonSection.from_config(request_config)
    except AttributeError as e:
        logger.error('Common section is invalid: {}'.format(e.args[0]))
        valid = False
        messages.append(e.args[0])

    try:
        DataSection.from_config(request_config)
    except AttributeError as e:
        logger.error('Data section is invalid: {}'.format(e.args[0]))
        valid = False
        messages.append(e.args[0])

    try:
        InventorySection.from_config(request_config)
    except AttributeError as e:
        logger.error('Inventory section is invalid: {}'.format(e.args[0]))
        valid = False
        messages.append(e.args[0])

    try:
        MiscSection.from_config(request_config)
    except AttributeError as e:
        logger.error('Misc section is invalid: {}'.format(e.args[0]))
        valid = False
        messages.append(e.args[0])

    request = Request.from_config(request_config)

    valid_streams, streams_messages = validate_streams(request)
    messages.extend(streams_messages)
    valid = valid_streams and valid

    try:
        if request.common.is_relaxed_cmor():
            logger.info('Relaxed CMOR is activated. Skip CV validations.')
        else:
            validate_request(request)
    except AttributeError as e:
        logger.error('Cannot validate request against CV because sections are invalid')
        valid = False
    except CVPathError as e:
        logger.error(e.args[0])
        valid = False
        messages.append(e.args[0])
    except CVEntryError as e:
        logger.error('Failed to pass against CV: {}'.format(e.args[0]))
        valid = False
        messages.append(e.args[0])

    if valid:
        logger.info('Request configuration is valid.')

    return valid, messages


def validate_streams(request: Request) -> Tuple[bool, List[str]]:
    logger = logging.getLogger(__name__)

    plugin = PluginStore.instance().get_plugin()
    model_parameters = plugin.models_parameters(request.metadata.model_id)
    available_streams = model_parameters.streams()

    valid = True
    messages = []
    for stream in request.data.streams:
        if stream not in available_streams:
            error_message_template = 'Stream {} is not in the model parameters specified and cannot be proceesed'
            logger.error(error_message_template.format(stream))
            valid = False
            messages.append(error_message_template.format(stream))
    return valid, messages
