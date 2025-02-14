# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
'''
Tools for interfacing with the cdds convert workflow.
'''
from configparser import ConfigParser
import json
import os
import subprocess

from cdds.convert.exceptions import (SuiteCheckoutError,
                                     SuiteConfigMissingValueError,
                                     WorkflowSubmissionError)
from cdds.common import run_command


def update_suite_conf_file(filename, section_name, changes_to_apply, raw_value=False, delimiter="="):
    """
    Update the contents of a rose suite configuration file, on disk,
    based on supplied keywords.

    Parameters
    ----------
    filename : str
        Name of the file to update.
    section_name : str
        The section of the rose-suite.conf to apply changes to.
    changes_to_apply : dict
        A dictionary containing field_name:field_value pairs.
    raw_value : bool
        If False, format values using json.dumps.
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
    section = parser[section_name]
    changes = []
    for field, new_value in changes_to_apply.items():
        if not raw_value:
            new_value = json.dumps(new_value)
        if field not in section:
            raise SuiteConfigMissingValueError('Field "{}" not found in "{}".'
                                               ''.format(field, filename))
        if section[field] != new_value:
            try:
                changes.append((field, str(section[field]),
                                str(new_value)))
                section[field] = new_value
            except TypeError as error:
                msg = ('Failed attempting to set field "{}" to "{}": '
                       '').format(field, repr(new_value))
                raise TypeError(msg + str(error))

    parser.write(open(filename, 'w'))
    return changes


def run_workflow(location, simulation=False, cylc_args=None, env=None):
    """
    Run a cylc workflow using vip and return the standard output.

    Parameters
    ----------
    location : str
        Location to submit the cylc workflow from (i.e. where the workflow
        has been checked out to).
    simulation : bool
        Set to true to play workflow in simulation mode (for testing).
    cylc_args : list of str
        Arguments to include in the call to cylc vip-run. This list
        is prefixed with ['--mode=simulation'] if `simulation`
        is set.
    env : dict
        Environment variables to be set when rose is run. Should be a
        copy of `os.environ`.

    Returns
    -------
    tuple
        The text returned by the cylc vip command (stdout,
        stderr).

    Raises
    ------
    AssertionError
        If `location` does not exist.
    WorkflowSubmissionError
        If an error occured when submitting the workflow.
    """
    assert os.path.exists(location), 'location not found'

    # identify the workflow name
    for argument in cylc_args:
        if argument.startswith("--workflow-name"):
            workflow_name = argument.split("=")[1]
    # clean an existing workflow if it exists
    clean_command = ['cylc', 'clean', workflow_name]
    run_command(clean_command)

    # construct the command for running the workflow
    install_command = ['cylc', 'vip', location]
    install_command += cylc_args

    if simulation:
        install_command += ['--mode=simulation']

    install_command += ['--no-run-name']

    result = run_command(install_command, "Running workflow failed", WorkflowSubmissionError)

    return result
