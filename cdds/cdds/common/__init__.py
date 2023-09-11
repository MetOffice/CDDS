# (C) British Crown Copyright 2017-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`common` module contains common library functions used by
other packages.
"""
import copy
import grp
import hashlib
import json
import logging
import os
import platform
import re
import subprocess
import time
from collections import defaultdict
from datetime import datetime
from distutils.version import StrictVersion
from functools import partial, wraps
from typing import Any, Callable, List, Optional, Tuple, Type, Union

from cftime import datetime as cf_datetime
from metomi.isodatetime.data import Calendar, TimePoint
from metomi.isodatetime.parsers import DurationParser, TimePointParser, TimeRecurrenceParser


from cdds.common.old_request import read_request
from cdds.convert.exceptions import IncompatibleCalendarMode
from cdds.common.constants import (
    CDDS_DEFAULT_DIRECTORY_PERMISSIONS, DATE_TIME_REGEX, ROSE_URLS,
    VARIANT_LABEL_FORMAT, LOG_TIMESTAMP_FORMAT, SUPPORTED_CALENDARS)


def get_log_datestamp():
    return datetime.utcnow().strftime(LOG_TIMESTAMP_FORMAT)


def configure_logger(log_name, log_level, append_log, threaded=False,
                     datestamp=None, stream=None):
    """
    Create the configured logger.

    Parameters
    ----------
    log_name: string
        The name of the log.
    log_level: integer
        The level of the log (see :meth:`logging.Logger.setLevel`).
    append_log: boolean
        Whether to append to the log.
    threaded: bool, optional
        Include thread name (processName) in log Formatter.
    stream: str, optional
        If specified include in the log name
    """
    # Determine whether to append to the log.
    log_mode = 'w'
    if append_log:
        log_mode = 'a'
    if log_name:
        if datestamp is None:
            datestamp = get_log_datestamp()
        if stream:
            log_name = '{}_{}_{}.log'.format(log_name, stream, datestamp)
        else:
            log_name = '{}_{}.log'.format(log_name, datestamp)

    # Create the logger (do not give the root logger a name!).
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.captureWarnings(True)

    # Remove any current handlers; the handlers persist within the same
    # Python session, so ensure the root logger is 'clean' every time
    # this function is called. Note that using logger.removeHandler()
    # doesn't work reliably e.g., when running setup.py nosetests.
    logger.handlers = []

    # Create a file handler for the logger.
    if log_name:
        file_handler = logging.FileHandler(log_name, log_mode)
        file_handler.setLevel(logging.DEBUG)
        if threaded:
            file_formatter = logging.Formatter(
                '%(asctime)s %(name)s.%(funcName)s %(processName)s '
                '%(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s %(name)s.%(funcName)s %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        # Configure the logger by adding the file handler.
        logger.addHandler(file_handler)

    # Create a console handler for the logger.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    # Configure the logger by adding the console handler.
    logger.addHandler(console_handler)


def common_command_line_args(parser, default_log_name, log_level, version):
    """
    Add the common command line arguments to the argument parser.

    Parameters
    ----------
    parser: :class:`argparse.ArgumentParser` object
        The argument parser to be added to.
    default_log_name: str
        The default name of log file.
    log_level: integer
        The level of the log (see :meth:`logging.Logger.setLevel`).
    version: str
        The version of the command line script.
    """
    parser.add_argument(
        '-l', '--log_name', default=default_log_name, help=(
            'The name of the log file. The log file will be written to the '
            'current working directory unless the full path is provided. Set '
            'the value to an empty string to only send messages to the screen '
            'i.e., do not create a log file.'))
    parser.add_argument(
        '-a', '--append_log', action='store_true', help=(
            'Append to the log, rather than overwrite.'))
    parser.set_defaults(log_level=log_level)
    log_level_group = parser.add_mutually_exclusive_group()
    log_level_group.add_argument(
        '-v', '--verbose', action='store_const', const=logging.DEBUG,
        help='Verbose (debug) logging.', dest='log_level')
    log_level_group.add_argument(
        '-q', '--quiet', action='store_const', const=logging.WARNING,
        help='Quiet (warning) logging.', dest='log_level')
    parser.add_argument(
        '--version', action='version', version=(
            '%(prog)s {version}'.format(version=version)))


def mass_output_args(parser, output_mass_suffix, output_mass_root):
    help_msg = ('Sub-directory in MASS to use when moving data. This '
                'directory is appended to the default root CDDS mass '
                'location - {cdds_mass}. '
                ''.format(cdds_mass=output_mass_suffix))
    parser.add_argument('--output_mass_suffix',
                        default=output_mass_suffix,
                        help=help_msg)
    help_msg = ('Full path to the root mass location to use for archiving the '
                'output data.')
    parser.add_argument('--output_mass_root',
                        default=output_mass_root,
                        help=help_msg)


def root_dir_args(parser, default_root_proc_dir, default_root_data_dir):
    """
    Add arguments relating to the root cdds directories to the argument parser
    object.

    Parameters
    ----------
    parser: :class:`argparse.ArgumentParser` object
        The argument parser to be added to.
    default_root_proc_dir: str
        The root path to the proc directory.
    default_root_data_dir: str
        The root path to the data directory.
    """
    parser.add_argument(
        '-c', '--root_proc_dir', default=default_root_proc_dir, help=(
            'The root path to the proc directory.'))
    parser.add_argument(
        '-t', '--root_data_dir', default=default_root_data_dir, help=(
            'The root path to the data directory.'))


def meta_dir_args(parser, default_standard_names_dir):
    """
    Add arguments relating to the cdds directories containing metadata
    to the argument parser object.

    Parameters
    ----------
    parser: :class:`argparse.ArgumentParser` object
        The argument parser to be added to.
    default_standard_names_dir: str
        The root path to the standard names table directory.
    """
    parser.add_argument(
        '-S', '--standard_names_dir', default=default_standard_names_dir,
        help=('The root path to the standard names table directory.'))


def determine_rose_suite_url(suite_id, internal=True):
    """
    Return the URL for the Rose suite.

    Parameters
    ----------
    suite_id: str
        The |suite identifier|.
    internal: bool
        Whether internal access is allowed.

    Returns
    -------
    : str
        The URL for the Rose suite.

    Raises
    ------
    ValueError
        If the |suite identifier| does not contain a ``-``.

    Examples
    --------
    >>> determine_rose_suite_url('u-abcde')
    'svn://fcm1/roses-u.xm_svn/a/b/c/d/e/'

    >>> determine_rose_suite_url('u-abcde', internal=False)
    'https://code.metoffice.gov.uk/svn/roses-u/a/b/c/d/e/'

    >>> determine_rose_suite_url('mi-abcde')
    'svn://fcm1/roses_mi_svn/a/b/c/d/e/'

    >>> determine_rose_suite_url('abcde')
    Traceback (most recent call last):
      ...
    ValueError: Unable to determine the URL from suite id "abcde"
    """
    if '-' not in suite_id:
        raise ValueError(
            'Unable to determine the URL from suite id "{}"'.format(suite_id))
    location, name = suite_id.split('-')
    if internal:
        root_url = ROSE_URLS[location]['internal']
    else:
        root_url = ROSE_URLS[location]['external']
    url = '{}/{}/'.format(root_url, '/'.join(name))
    return url


def check_svn_location(svn_url):
    """
    Return True if the supplied svn location is accessible.

    Parameters
    ----------
    svn_url : str

    Returns
    -------
    : bool
        True if svn location is accessible
    """
    command = ['svn', 'ls', svn_url, '--depth', 'empty']
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    proc.communicate()
    return proc.returncode == 0


def run_command(command, msg=None, exception=None, environment=None):
    """
    Run the command in a new process using :class:`subprocess.Popen`.

    Parameters
    ----------
    command: list of strings
        The command to run.
    msg: string
        The message used to provide more information if a non-zero
        return code is returned.
    exception: Exception
        The exception used if a non-zero return code is returned; if
        None, RuntimeError is used.
    environment: dictionary
        The environment variables for the new process; if None, the
        the current process' environment is inherited.

    Returns
    -------
    : str
        The standard output from the command.
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               env=environment, universal_newlines=True)
    (stdoutdata, stderrdata) = process.communicate()
    return_code = process.returncode
    if return_code != 0:
        msg_format = 'Problem running command "{}" (return code: {}): {}'
        if msg is None:
            exc_msg = msg_format.format(' '.join(command), return_code, stderrdata)
        else:
            exc_msg = msg_format.format(' '.join(command), return_code, '{}: {}'.format(msg, stderrdata))
        if exception is None:
            exception = RuntimeError
        raise exception(exc_msg)
    return stdoutdata


def construct_string_from_facet_string(facet_string, facet_values,
                                       string_type='path'):
    """
    Return the constructed string as described by the ``facet_string``
    and the ``facet_values``.

    ``string_type`` can be either ``path`` or ``filename``;
    :func:`os.path.join` is used to join the facets if ``string_type``
    is equal to ``path``, while ``_`` is used to join the facets if
    ``string_type`` is equal to ``filename``.

    Parameters
    ----------
    facet_string: str
        Names separated by ``|``
    facet_values: dict
        Values corresponding to the names

    Returns
    -------
    : str
        The constructed string as described by the ``facet_string`` and
        the ``facet_values``.

    Raises
    ------
    RuntimeError:
        If ``string_type`` is not equal to either ``path`` or
        ``filename``.
    ValueError:
        If a facet from the ``facet_string`` does not have a
        corresponding ``facet_value``.

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
    """
    logger = logging.getLogger(__name__)
    if string_type not in ['path', 'filename']:
        raise RuntimeError(
            'string_type must be either "path" or "filename"')
    facets = []
    for facet in facet_string.split('|'):
        if facet not in facet_values:
            raise ValueError(
                'Unable to construct path; "{}" not available'.format(facet))
        facet_value = str(facet_values[facet])
        if ' ' in facet_value:
            new_facet_value = facet_value.split(' ')[0]
            logger.debug('Found value "{}" for facet "{}". Using "{}"'.format(facet_value, facet, new_facet_value))
            facet_value = new_facet_value
        facets.append(facet_value)
    if string_type == 'path':
        constructed_string = os.path.join(*facets)
    else:
        constructed_string = '_'.join(facets)
    return constructed_string


def update_permissions(path, group, permissions=None):
    """
    Set the group and permissions for the file or directory at location path.

    Parameters
    ----------
    path: str
        The full path to the directory to be created.
    group: str
        The name of the group to use when creating the directory.
    permissions: int
        The permissions to set for this directory, in octal format (e.g. 0775).
        If none, the default is CDDS_DEFAULT_DIRECTORY_PERMISSIONS.

    Returns
    -------
    None
    """
    logger = logging.getLogger(__name__)
    try:
        gid = grp.getgrnam(group).gr_gid
    except (TypeError, KeyError):
        gid = None
    if gid is None:
        # if no gid found, return without changing permissions or ownership
        return

    # set ownership
    try:
        os.chown(path, -1, gid)  # Leave uid unchanged.
        logger.debug(
            'Group of "{}" changed to "{}"'.format(path, group))
    except OSError:
        logger.debug(
            'Unable to change group of "{}"'.format(path))
    # set permissions
    if permissions is None:
        permissions = CDDS_DEFAULT_DIRECTORY_PERMISSIONS
    try:
        os.chmod(path, permissions)
        logger.debug(
            'Mode of "{}" changed to "{}"'.format(path, oct(permissions)))
    except OSError:
        logger.info(
            'Unable to change mode of "{}"'.format(path))


def create_directory(path, group=None, permissions=None, root_dir=None):
    """
    Create the directory ``path`` owned by ``group``, if specified.

    If the directory already exists and ``group`` is specified, the
    ``group`` of the directory will be updated.

    If the ``group`` is updated, the permissions of the directory will
    also be updated so that the directory is read, write and executable
    by the ``group``.

    Parameters
    ----------
    path: str
        The full path to the directory to be created.
    group: str
        The name of the group to use when creating the directory.
    permissions: int
        The permissions to set for this directory, in octal format (e.g. 0775).
        If none, the default is CDDS_DEFAULT_DIRECTORY_PERMISSIONS.
    root_dir: str
        The path to the root of the CDDS directory. No directories higher
        up the directory structure will have permissions or ownership changed.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    if os.path.isdir(path):
        logger.warning('Directory "{}" already exists'.format(path))
    else:
        os.makedirs(path)
        logger.debug('Created directory "{}"'.format(path))

    dirs_to_change = get_directories(path, root_dir)
    for dirpath in dirs_to_change:
        update_permissions(dirpath, group, permissions)


def get_directories(path, root_dir=None):
    """
    Return the directories that make up the path provided to the ``path``
    parameter.

    Parameters
    ----------
    path: str
        The path to get the directories from.
    root_dir: str
        The path to the root of the CDDS directory. No directories higher
        up the directory structure be returned in the directory list.


    Returns
    -------
    : str
        The directories.

    Examples
    --------
    >>> get_directories('my/test/path')
    ['my', 'my/test', 'my/test/path']

    >>> get_directories('/starts/with/sep')
    ['/starts', '/starts/with', '/starts/with/sep']
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


def check_directory(directory):
    """
    Return the full path to the directory provided to the ``directory``
    parameter after checking the directory exists.

    Parameters
    ----------
    directory: str
        The name of the directory to be checked.

    Returns
    -------
    : str
        The full path to the directory.

    Raises
    ------
    OSError:
        If the directory does not exist.

    Examples
    --------
    >>> check_directory('non_existant_directory')
    Traceback (most recent call last):
      ...
    OSError: Directory "non_existant_directory" does not exist
    """
    if not os.path.isdir(directory):
        raise OSError(
            'Directory "{}" does not exist'.format(directory))
    return os.path.abspath(directory)


def check_file(filename):
    """
    Check whether the file provided to the ``filename`` parameter
    exists.

    Parameters
    ----------
    filename: string
        The name of the file to be checked.

    Raises
    ------
    IOError:
        If the file does not exist.
    """
    if not os.path.isfile(filename):
        raise IOError(
            'File "{filename}" does not exist'.format(filename=filename))


def check_files(filenames_string):
    """
    Check whether the files provided to the ``filenames_string`` parameter
    exist. This checker will split the string before checking for each file.

    Parameters
    ----------
    filenames_string: string
        The space separated list of filenames to be checked.

    Raises
    ------
    IOError:
        If the file does not exist.
    """
    for filename in filenames_string.split():
        if not os.path.isfile(filename):
            raise IOError(
                'File "{filename}" does not exist'.format(filename=filename))


def check_date_format(date, date_regex=DATE_TIME_REGEX):
    """
    Ensure the date provided to the ``date``` parameter has a format
    that is equal to the regular expression provided to the
    ``date_regex`` parameter.

    Parameters
    ----------
    date: string
        The date to be checked.
    date_regex: string
        The regular expression describing the format of the date.

    Raises
    ------
    ValueError:
        If the date does not match the format.

    Examples
    --------
    >>> check = check_date_format('1970-01-01T00:00:00')
    >>> if check is None:
    ...     print('Date format correct')
    Date format correct

    >>> check = check_date_format(
    ...     '01011970',
    ...     '(?P<day>\\d{2})(?P<month>\\d{2})(?P<year>\\d{4})')
    >>> if check is None:
    ...     print('Date format correct')
    Date format correct

    >>> check_date_format('1970-01-01T00:00:00',
    ...     '(?P<year>\\d{4})-(?P<month>\\d{2})-(?P<day>\\d{2})')
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: Date "1970-01-01T00:00:00" does not match
      "(?P<year>\\d{4})-(?P<month>\\d{2})-(?P<day>\\d{2})"
    """
    matched = re.compile('^{}$'.format(date_regex)).match(date)
    if not date.upper() == 'N/A' and not matched:
        msg = (
            'Date "{date}" does not match "{date_regex}"'.format(
                date=date, date_regex=date_regex))
        raise ValueError(msg)


def check_run_bounds_format(run_bounds):
    """
    Ensure the run bounds provided to the ``run_bounds`` parameter has
    the correct format.

    The run bounds must be in the form
    ``%Y-%m-%dT%H:%M:%S %Y-%m-%dT%H:%M:%S``.

    Parameters
    ----------
    run_bounds: string
        The run bounds.

    Raises
    ------
    ValueError:
        If the run bounds does not match the format.

    Examples
    --------
    >>> check = check_run_bounds_format(
    ...     '1950-03-10T00:00:00 1950-03-20T00:00:00')
    >>> if check is None:
    ...     print('Run bounds format correct')
    Run bounds format correct

    >>> check = check_run_bounds_format('1950-03-10T00:00:00')
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    ValueError: Run bounds "1950-03-10T00:00:00" does not match the
      expected format (not enough values to unpack (expected 2, got 1))

    >>> check = check_run_bounds_format(
    ...     '1950-03-10T00:00:00 1950-03-20 00:00:00')
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
     ...
    ValueError: Run bounds "1950-03-10T00:00:00 1950-03-20 00:00:00"
      does not match the expected format (too many values to unpack (expected 2))
    """
    try:
        start_date, end_date = run_bounds.split()
    except ValueError as err:
        msg = ('Run bounds "{run_bounds}" does not match the expected '
               'format ({err})'.format(run_bounds=run_bounds, err=err))
        err.args = (msg,)
        raise
    check_date_format(start_date, DATE_TIME_REGEX)
    check_date_format(end_date, DATE_TIME_REGEX)


def check_variant_label_format(variant_label):
    r"""
    Ensure the |variant label| provided to the ``variant_label``
    parameter has the correct format.

    The |variant label| must be in the form
    ``r(\d+)i(\d+)p(\d+)f(\d+)``.

    Parameters
    ----------
    variant_label: string
        The |variant label|.

    Raises
    ------
    ValueError:
        If the |variant label| does not match the format.

    Examples
    --------
    >>> check = check_variant_label_format('r1i1p1f1')
    >>> if check is None:
    ...     print('Variant label format correct')
    Variant label format correct

    >>> check = check_variant_label_format('r1p2i3f4')
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: Variant label "r1p2i3f4" does not match the expected
      format

    >>> check = check_variant_label_format('r3i2p1')
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: Variant label "r3i2p1" does not match the expected format
    """
    pattern = re.compile(VARIANT_LABEL_FORMAT)
    match = pattern.match(variant_label)
    if not match:
        msg = ('Variant label "{}" does not match the expected format'
               ''.format(variant_label))
        raise ValueError(msg)


def check_number(value):
    """
    Check whether the value provided to the ``value`` parameter
    is a number, or can be converted into a number.

    Parameters
    ----------
    value:
        The value to be checked.

    Raises
    ------
    TypeError:
        If ``value`` is not a number.

    Examples
    --------
    >>> check_number(3)

    >>> check_number(4.56)

    >>> check_number(1e-7)

    >>> check_number('3')

    >>> check_number('some string')
    Traceback (most recent call last):
      ...
    TypeError: "some string" is not a number
    """
    try:
        float(value)
    except ValueError:
        raise TypeError('"{}" is not a number'.format(value))


def compare_versions(version_to_compare, version_with_expression):
    """
    Return whether the ``version_to_compare`` falls in the
    ``version_with_expression``.

    Parameters
    ----------
    version_to_compare: string
        The version to compare.
    version_with_expression: string
        The version with the expression.

    Returns
    -------
    : boolean
        The result of the expression.
    """
    lt_gt_pattern = re.compile(r'(^[<=>]{1,2}?)\s*(\d+\.\d+\.?\d*?)')
    ranges_pattern = re.compile(r'(\d+\.\d+\.?\d*?)\s*\-\s*(\d+\.\d+\.?\d*?)')
    lt_gt_match = lt_gt_pattern.match(version_with_expression)
    ranges_match = ranges_pattern.match(version_with_expression)
    if lt_gt_match:
        equation = (
            'StrictVersion("{version_to_compare}"){symbol}'
            'StrictVersion("{version}")'.format(
                version_to_compare=version_to_compare,
                symbol=lt_gt_match.group(1), version=lt_gt_match.group(2)))
    elif ranges_match:
        equation = (
            'StrictVersion("{min_version}")<='
            'StrictVersion("{version_to_compare}")<='
            'StrictVersion("{max_version}")'.format(
                min_version=ranges_match.group(1),
                version_to_compare=version_to_compare,
                max_version=ranges_match.group(2)))
    else:
        raise RuntimeError(
            'No support available for version with the format '
            '"{version_with_expression}"'.format(
                version_with_expression=version_with_expression))
    return eval(equation)


def remove_newlines(value):
    """
    Return the value with new lines replaced with a single whitespace.

    Parameters
    ----------
    value: string
        The value.

    Returns
    -------
    : string
        The value with new lines replaced with a single whitespace.

    Examples
    --------
    >>> value = 'This\\nhas\\nmany\\nnew\\nlines.'
    >>> print(remove_newlines(value))
    This has many new lines.
    """
    return value.replace('\n', ' ')


def netCDF_regexp(model_component=None, substream=None, ens_id=None):
    """
    Return a regular expression matching netCDF filenames.

    Parameters
    ----------
    model_component: string
        If set, the regular expression will match provided
        model component (nemo, cice or medusa).
    substream: string
        If set, the regular expression will match provided
        substream.
    ens_id: string
        If set, the regular expression will handle filenames with
        ensemble_id.
    Returns
    -------
    : str
        Regular expression.
    """
    if model_component is None:
        model_component = r"([a-z]+)"
    else:
        model_component = r"({})".format(model_component)
    if ens_id is None:
        suite = r".{5}"
    else:
        suite = r".{5}\-[a-zA-Z0-9\-]+"
    frequency = r".{2}"
    date_range = r"(\d{8})-(\d{8})"
    domain_id = r"[io]"
    if substream is None:
        substream = r"([a-zA-Z0-9\-]+){0,1}"
        sep = r"_{0,1}"
    else:
        substream = r"({})".format(substream)
        sep = "_"
    extension = r"\.nc$"

    return "{}_{}{}_{}_{}{}{}{}".format(
        model_component, suite, domain_id, frequency, date_range,
        sep, substream, extension)


def set_checksum(dictionary, overwrite=True):
    """
    Calculate the checksum for the ``dictionary``, then add the
    value to ``dictionary`` under the ``checksum`` key. ``dictionary``
    is modified in place.

    Parameters
    ----------
    dictionary: dict
        The dictionary to set the checksum to.
    overwrite: bool
        Overwrite the existing checksum (default True).

    Raises
    ------
    RuntimeError
        If the ``checksum`` key already exists and ``overwrite`` is
        False.
    """
    if 'checksum' in dictionary:
        if not overwrite:
            raise RuntimeError('Checksum already exists.')
        del dictionary['checksum']
    checksum = _checksum(dictionary)
    dictionary['checksum'] = checksum


def validate_checksum(dictionary):
    """
    Validate the checksum in the ``dictionary``.

    Parameters
    ----------
    dictionary: dict
        The dictionary containing the ``checksum`` to validate.

    Raises
    ------
    KeyError
        If the ``checksum`` key does not exist.
    RuntimeError
        If the ``checksum`` value is invalid.
    """
    if 'checksum' not in dictionary:
        raise KeyError('No checksum to validate')
    dictionary_copy = copy.deepcopy(dictionary)
    del dictionary_copy['checksum']
    checksum = _checksum(dictionary_copy)
    if dictionary['checksum'] != checksum:
        msg = ('Expected checksum   "{}"\n'
               'Calculated checksum "{}"').format(dictionary['checksum'],
                                                  checksum)
        raise RuntimeError(msg)


def _checksum(obj):
    obj_str = json.dumps(obj, sort_keys=True)
    checksum_hex = hashlib.md5(obj_str.encode('utf8')).hexdigest()
    return 'md5: {}'.format(checksum_hex)


DT_ELEMENTS = ['year', 'month', 'day', 'hour', 'minute', 'second']


def get_most_recent_file(dir_to_search, key_str, pattern_str):
    """
    Look for the most recent file in a given directory that matches a
    pattern like "<prefix>_YYYY-MM-DDTHHMMDD.<ext>.

    Parameters
    ----------
    dir_to_search: str
        The directory to look in.
    key_str: str
        The string that all filenames of interest contain.
    pattern_str: str
        A regular expression string that matches all filenames of interest.
        The regular expression must include groups for each of the six
        datetime components: year, month, day, hour, minute and second, so that
        the files can be sorted by date.

    Returns
    -------
    : str
        The full path to the most recent matching file in the directory.

    """
    file_list = [filename for filename in os.listdir(dir_to_search) if
                 key_str in filename]
    regex_pattern = re.compile(pattern_str)
    dt_list = []
    file_dict = {}
    path_most_recent = None
    for candidate in file_list:
        match = regex_pattern.match(candidate)
        if match:
            file_dt = datetime(
                *[int(match.group(el)) for el in DT_ELEMENTS])
            dt_list += [file_dt]
            file_dict[file_dt] = candidate
    if len(dt_list) > 0:
        path_most_recent = os.path.join(dir_to_search,
                                        file_dict[sorted(dt_list)[-1]])
    return path_most_recent


def get_most_recent_file_by_stream(dir_to_search, key_str, pattern_str):
    """
    Look for the most recent file in a given directory that matches a
    pattern like "<prefix>_<stream>_YYYY-MM-DDTHHMMDD.<ext> and return
    a dictionary with results by stream.

    Parameters
    ----------
    dir_to_search: str
        The directory to look in.
    key_str: str
        The string that all filenames of interest contain.
    pattern_str: str
        A regular expression string that matches all filenames of interest.
        The regular expression must include groups for each of the six
        datetime components: year, month, day, hour, minute and second, so that
        the files can be sorted by date.

    Returns
    -------
    : dict
        The full path to the most recent matching file in the directory for each stream.
        The key ``None`` will be used if all streams are included in a file.
    """
    file_list = [filename for filename in os.listdir(dir_to_search) if
                 key_str in filename]
    regex_pattern = re.compile(pattern_str)
    # set up dictionaries
    dt_list_by_stream = defaultdict(list)
    file_dict = defaultdict(dict)

    for candidate in file_list:
        match = regex_pattern.match(candidate)
        if match:
            stream = match.group('stream')
            file_dt = datetime(
                *[int(match.group(el)) for el in DT_ELEMENTS])
            dt_list_by_stream[stream].append(file_dt)
            file_dict[stream][file_dt] = candidate
    path_most_recent_by_stream = {}
    for stream, dt_list in dt_list_by_stream.items():
        if len(dt_list) > 0:
            most_recent_file = file_dict[stream][sorted(dt_list)[-1]]
            path_most_recent_by_stream[stream] = os.path.join(dir_to_search, most_recent_file)
    return path_most_recent_by_stream


def cmp(a, b):
    """
    Provides functionality equivalent to Python2 cmp() function.

    Parameters
    ----------
    a:
        First object to compare.
    b:
        Second object to compare.

    Returns
    -------
    : int
        -1 if a < b, 0 if 0 == 0, 1 if a > b
    """
    return (a > b) - (a < b)


def retry(func: Optional[Callable] = None, exception: Type[Exception] = Exception, retries: int = 3
          ) -> Union[Callable, Tuple[bool, Callable]]:  # ignore: type
    """
    Retry decorator with exponential backoff.

    For more decorator documentation, see:
    https://www.python.org/dev/peps/pep-0318/
    https://realpython.com/primer-on-python-decorators/

    :param func: Callable on which the decorator is applied, by default None
    :type func: typing.Callable, optional
    :param exception: Exception(s) that invoke retry, by default Exception
    :type exception: Exception or tuple of exceptions, optional
    :param retries: Number of tries before giving up, by default 3
    :type retries: int, optional
    :return: Decorated callable that calls itself when exception(s) occur.
    :rtype: typing.Callable
    """
    if func is None:
        return partial(retry, exception=exception, retries=retries)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Tuple[bool, Union[Callable, None]]:
        max_retries = retries
        if func is None:
            return True, func

        while max_retries > 1:
            try:
                return True, func(*args, **kwargs)
            except exception as e:
                func_name = getattr(func, "__name__", "Unknown")
                logging.warning("Unable to perform job '{}': {}. Retrying again...".format(func_name, e))
                max_retries -= 1

        return False, func(*args, **kwargs)

    return wrapper


def set_calendar(request_file: str):
    """ Set the metomi.isodatetime calendar based on a request.json file.

    :param request_file: Path to a request.json file.
    :type request_file: str
    :raises IncompatibleCalendarMode:
    """
    request = read_request(request_file)

    if request.calendar in SUPPORTED_CALENDARS:
        Calendar.default().set_mode(request.calendar)
    else:
        raise IncompatibleCalendarMode


def generate_datestamps_pp(start_date: str,
                           end_date: str,
                           file_frequency: str) -> Tuple[List[str], List[TimePoint]]:
    """ Generate common datestamp strings used by .pp files.

    :param start_date: ISO formatted string e.g, 19890101 (Inclusive)
    :type start_date: str
    :param end_date: ISO formatted string e.g, 19890101 (Exclusive)
    :type end_date: str
    :param file_frequency: Maps to a duration and format string
    :type file_frequency: str
    :return: A tuple of list of datestamps and list of timepoints
    :rtype: Tuple[List[str], List[TimePoint]]
    :raises IncompatibleCalendarMode:
    """

    modes = {"daily": ["P1D", "%Y%m%d"],
             "10 day": ["P10D", "%Y%m%d"],
             "monthly": ["P1M", "%Y%b"],
             "season": ["P3M", "%Y"]}

    seasons = {3: "mam", 6: "jja", 9: "son", 12: "djf"}

    calendar = Calendar.default().mode

    if calendar in ["gregorian"] and file_frequency == "10 day":
        raise IncompatibleCalendarMode

    duration, date_format = modes[file_frequency]
    timepoints = generate_time_points(start_date, end_date, duration)
    datestamps = []

    for timepoint in timepoints:
        # The TimePoint object has to be converted to a cf_datetime object to make use of the full
        # strptime specification.
        cf_timepoint = cf_datetime.strptime(str(timepoint), "%Y-%m-%dT%H:%M:%SZ", calendar=calendar)
        if file_frequency != "season":
            datestamp = cf_timepoint.strftime(date_format).lower()
        else:
            datestamp = cf_timepoint.strftime("%Y") + seasons[cf_timepoint.month]
        datestamps.append(datestamp)

    return datestamps, timepoints


def generate_datestamps_nc(start_date: str,
                           end_date: str,
                           file_frequency: str) -> Tuple[List[str], List[TimePoint]]:
    """Generate common datestamp stings used for .nc files.

    :param start_date: ISO formatted string e.g, 19890101 (Inclusive)
    :type start_date: str
    :param end_date: ISO formatted string e.g, 19890101 (Exclusive)
    :type end_date: str
    :param file_frequency: Maps to a duration and format string
    :type file_frequency: str
    :return: A tuple of list of datestamps and list of timepoints
    :rtype: Tuple[List[str], List[TimePoint]]
    """

    modes = {"monthly": ["P1M", "%Y%m%d"],
             "quarterly": ["P3M", "%Y%m%d"]}

    calendar = Calendar.default().mode

    duration, date_format = modes[file_frequency]
    timepoints = generate_time_points(start_date, end_date, duration)
    datestamps = []

    for timepoint in timepoints:
        start = timepoint
        end = timepoint + DurationParser().parse(duration)
        start = cf_datetime.strptime(str(start), "%Y-%m-%dT%H:%M:%SZ", calendar=calendar)
        end = cf_datetime.strptime(str(end), "%Y-%m-%dT%H:%M:%SZ", calendar=calendar)
        datestamp = start.strftime(date_format) + "-" + end.strftime(date_format)
        datestamps.append(datestamp)

    return datestamps, timepoints


def generate_time_points(start_date: Union[str, TimePoint],
                         end_date: Union[str, TimePoint],
                         duration: str) -> List[TimePoint]:
    """A convenience function for generating a list of TimePoint objects.

    :param start_date: ISO style string or TimePoint (Inclusive)
    :type start_date: Union[str, TimePoint]
    :param end_date: ISO style string or TimePoint (Exclusive)
    :type end_date: Union[str, TimePoint]
    :param duration: ISO formatted duration string
    :type duration: str
    :return: List of TimePoint objects
    :rtype: List[TimePoint]
    """
    if isinstance(start_date, TimePoint):
        start_date = str(start_date)

    if isinstance(end_date, str):
        end_date = TimePointParser().parse(end_date)

    recurrence_string = f"R/{start_date}/{duration}"
    time_recurrence = TimeRecurrenceParser().parse(recurrence_string)

    time_points = []

    for time_point in time_recurrence:
        if time_point < end_date:
            time_points.append(time_point)
        else:
            break

    return time_points
