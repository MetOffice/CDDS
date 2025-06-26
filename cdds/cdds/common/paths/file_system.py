# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module to modify and manage the UNIX file system
"""
import grp
import logging
import os

from enum import Enum
from typing import Dict


CDDS_DEFAULT_DIRECTORY_PERMISSIONS = 0o775


class PathType(Enum):
    """
    Represents a given path type, e.g.
     - PATH, e.g. /path/to/dir/
     - FILENAME, e.g. test_file.txt
    """
    PATH = 'path'
    FILE_NAME = 'filename'


def construct_string_from_facet_string(facet_string: str, facet_values: Dict[str, str],
                                       string_type: PathType = PathType.PATH) -> str:
    """
    Return the constructed string as described by the ``facet_string`` and the ``facet_values``.

    ``string_type`` can be either ``path`` or ``filename``;
    :func:`os.path.join` is used to join the facets if ``string_type`` is equal to ``path``,
    while ``_`` is used to join the facets if ``string_type`` is equal to ``filename``.

    Examples
    --------
    >>> facet_values = {'project': 'CMIP', 'experiment': 'amip',
    ...                 'package': 'phase1'}
    >>> construct_string_from_facet_string(
    ...     'project|experiment|package', facet_values)
    'CMIP/amip/phase1'

    >>> construct_string_from_facet_string(
    ...     'experiment|package|project', facet_values,
    ...     string_type='filename')
    'amip_phase1_CMIP'

    :param facet_string: Names separated by ``|``
    :type facet_string: str
    :param facet_values: Values corresponding to the names
    :type facet_values: Dict[str, str]
    :param string_type: path or filename
    :type string_type: str
    :return:
    :rtype: list[str]
    """
    logger = logging.getLogger(__name__)
    facets = []
    for facet in facet_string.split('|'):
        if facet not in facet_values:
            raise ValueError('Unable to construct path; "{}" not available'.format(facet))
        facet_value = str(facet_values[facet])
        if ' ' in facet_value:
            new_facet_value = facet_value.split(' ')[0]
            logger.debug('Found value "{}" for facet "{}". Using "{}"'.format(facet_value, facet, new_facet_value))
            facet_value = new_facet_value
        facets.append(facet_value)
    if string_type == PathType.PATH:
        constructed_string = os.path.join(*facets)
    else:
        constructed_string = '_'.join(facets)
    return constructed_string


def create_directory(path: str) -> None:
    """
    Create the directory ``path`` if it does not exists.

    :param path: The full path to the directory to be created.
    :type path: str
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    if os.path.isdir(path):
        logger.warning('Directory "{}" already exists'.format(path))
    else:
        os.makedirs(path)
        logger.debug('Created directory "{}"'.format(path))


def get_directories(path: str, root_dir: str = None) -> list[str]:
    """
    Return the directories that make up the path provided to the ``path`` parameter.

    Examples
    --------
    >>> get_directories('my/test/path')
    ['my', 'my/test', 'my/test/path']

    >>> get_directories('/starts/with/sep')
    ['/starts', '/starts/with', '/starts/with/sep']

    :param path: The path to get the directories from.
    :type path: str
    :param root_dir: The path to the root of the CDDS directory. No directories higher
        up the directory structure be returned in the directory list.
    :type root_dir: str
    :return: The directories.
    :rtype: str
    """
    directories = []
    dir_list = [i1 for i1 in path.split(os.sep) if i1]
    dirpath = ''
    if root_dir:
        root_dir_list = [i1 for i1 in root_dir.split(os.sep) if i1]
        # check that the directory is a child of root_dir
        if root_dir_list == dir_list[:len(root_dir_list)]:

            dir_list = dir_list[len(root_dir_list):]
            dirpath = root_dir
        else:
            if path.startswith(os.sep):
                dirpath = os.sep
    else:
        if path.startswith(os.sep):
            dirpath = os.sep

    for directory in dir_list:
        dirpath = os.path.join(dirpath, directory)
        directories.append(dirpath)
    return directories
