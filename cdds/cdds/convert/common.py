# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import os
from datetime import datetime

from cdds.convert.exceptions import ArgumentError
from cdds.common.constants import DATESTAMP_PARSER_STR


def validate_archive_data_version(archive_data_version):
    """
    Checks if the archive data version has the expected date format. If not an exception will be raised

    :param archive_data_version: Archive data version as string
    :type archive_data_version: str
    """
    try:
        datetime.strptime(archive_data_version, DATESTAMP_PARSER_STR)
        return archive_data_version
    except ValueError:
        raise ArgumentError('Archive data version must have format "{}"'.format(DATESTAMP_PARSER_STR))


def expand_path(path: str) -> str:
    """
    Expands given path and returns the absolute path

    :param path:Paht to expand
    :type path: str
    :return: Absolute path
    :rtype: str
    """
    if path.startswith('~') or '$' in path:
        path = os.path.expanduser(os.path.expandvars(path))
    return os.path.abspath(path)
