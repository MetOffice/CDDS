# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
'''
Tools for interfacing with conversion Rose suite
'''
from configparser import ConfigParser
import json
import os
import subprocess

from cdds_convert.exceptions import (SuiteCheckoutError,
                                     SuiteConfigMissingValueError,
                                     SuiteSubmissionError,
                                     SuiteShutdownError)
from hadsdk.common import run_command


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


def checkout_url(svn_url, destination):
    """
    Checkout the contents of an SVN url to a given destination

    Parameters
    ----------
    svn_url : str
        SVN url to check out
    destination : str
        location to check out to

    Returns
    -------
    str
        standard output from svn command
    """
    cmd = ['svn', 'co', svn_url, destination]
    co_proc = subprocess.Popen(cmd, stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE, universal_newlines=True)
    output, error = co_proc.communicate()
    if co_proc.returncode != 0:
        msg = 'svn checkout failed.'
        msg += 'Command: "{}".'.format(' '.join(cmd))
        msg += 'stdout: "{}"'.format(output)
        msg += 'stderr: "{}"'.format(error)
        raise SuiteCheckoutError(msg)
    return output


def update_suite_conf_file(filename, delimiter="=", **kwargs):
    """
    Update the contents of a rose suite configuration file, on disk,
    based on supplied keywords.

    Parameters
    ----------
    filename : str
        Name of the file to update.
    delimiter : str, optional
        Character used for delimiting keys and values in the suite
        configuration file.

    Other keywords are used to specify changes to be made

    Returns
    -------
    list
        Each element is a 3-tuple with elements for the name of the
        field that is changed, the original value, and the new value.
    """
    parser = ConfigParser(delimiters=[delimiter])
    parser.optionxform = str
    parser.read(filename)
    section = parser['jinja2:suite.rc']
    changes = []
    for field, new_value in kwargs.items():
        new_value_str = json.dumps(new_value)
        if field not in section:
            raise SuiteConfigMissingValueError('Field "{}" not found in "{}".'
                                               ''.format(field, filename))
        if section[field] != new_value_str:
            try:
                changes.append((field, str(section[field]),
                                str(new_value_str)))
                section[field] = new_value_str
            except TypeError as error:
                msg = ('Failed attempting to set field "{}" to "{}": '
                       '').format(field, repr(new_value))
                raise TypeError(msg + str(error))

    parser.write(open(filename, 'w'))
    return changes


def submit_suite(location, simulation=False, rose_args=None, env=None):
    """
    Submit a suite and return the standard output.

    Parameters
    ----------
    location : str
        Location to submit the rose suite from (i.e. where the suite
        has been checked out to).
    simulation : bool
        Set to true to submit suite in simulation mode (for testing).
    rose_args : list of str
        Arguments to include in the call to rose suite-run. This list
        is prefixed with ['--', '--mode=simulation'] if `simulation`
        is set.
    env : dict
        Environment variables to be set when rose is run. Should be a
        copy of `os.environ`.

    Returns
    -------
    tuple
        The text returned by the rose suite-run command in (stdout,
        stderr).

    Raises
    ------
    AssertionError
        If `location` does not exist.
    SuiteSubmissionError
        If an error occurred when submitting the suite.
    """
    assert os.path.exists(location), 'location not found'
    command = ['rose', 'suite-run', '-C', location]
    if isinstance(rose_args, list):
        command += rose_args
    if simulation:
        command += ['--', '--mode=simulation']

    result = run_command(command, 'Rose suite-run command failed.',
                         SuiteSubmissionError, env)
    return result


def shutdown_suite(location, rose_args=None, env=None):
    """
    Shutdown a suite and return the standard output.

    Parameters
    ----------
    location : str
        Location to submit the rose suite from (i.e. where the suite
        has been checked out to).
    rose_args : list of str
        Arguments to include in the call to rose suite-shutdown.
    env : dict
        Environment variables to be set when rose is run. Should be a
        copy of `os.environ`.

    Returns
    -------
    tuple
        The text returned by the rose suite-run command in (stdout,
        stderr).

    Raises
    ------
    AssertionError
        If `location` does not exist.
    SuiteShutdownError
        If an error occurred when shutting down the suite.
    """
    assert os.path.exists(location), ('Suite location "{}" not found'
                                      ''.format(location))
    os.chdir(location)
    command = ['rose', 'suite-shutdown', '-y']
    if isinstance(rose_args, list):
        command += rose_args

    try:
        result = run_command(command, 'Rose shutdown command failed.',
                             SuiteShutdownError, env)
    except SuiteShutdownError as err:
        result = [str(err)]
    return result
