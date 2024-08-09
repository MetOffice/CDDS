# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
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
from cdds.common.request.inventory_section import InventorySection
from cdds.common.request.common_section import CommonSection
from cdds.common.request.data_section import DataSection
from cdds.common.configparser.interpolation import EnvInterpolation
from cdds.common.request.request_validations import validate_request
from cdds.common.request.validations.exceptions import CVPathError, CVEntryError


def do_request_validations(request_path: str) -> Tuple[bool, List[str]]:
    logger = logging.getLogger(__name__)
    valid = True
    messages = []

    interpolation = EnvInterpolation()
    request_config = ConfigParser(interpolation=interpolation, inline_comment_prefixes=('#',))
    request_config.optionxform = str  # Preserve case.
    request_config.read(request_path)
    load_cdds_plugins(request_config)

    calendar = request_config.get('metadata', 'calendar')
    Calendar.default().set_mode(calendar)

    try:
        MetadataSection.from_config(request_config)
    except AttributeError as e:
        logger.error('Metadata section is invalid.', e.args[0])
        valid = False
        messages.append(e.args[0])

    try:
        CommonSection.from_config(request_config)
    except AttributeError as e:
        logger.error('Common section is invalid.', e.args[0])
        valid = False
        messages.append(e.args[0])

    try:
        DataSection.from_config(request_config)
    except AttributeError as e:
        logger.error('Data section is invalid.', e.args[0])
        valid = False
        messages.append(e.args[0])

    try:
        InventorySection.from_config(request_config)
    except AttributeError as e:
        logger.error('Inventory section is invalid.', e.args[0])
        valid = False
        messages.append(e.args[0])

    try:
        request = Request.from_config(request_config)
        if request.common.is_relaxed_cmor():
            logger.info('Relaxed CMOR is activated. Skip CV validations.')
        else:
            validate_request(request)
    except AttributeError as e:
        logger.error('Cannot validate request against CV because sections are invalid.')
        valid = False
    except CVPathError as e:
        logger.error(e.args[0])
        valid = False
        messages.append(e.args[0])
    except CVEntryError as e:
        logger.error('Failed to pass against CV.', e.args[0])
        valid = False
        messages.append(e.args[0])

    return valid, messages
