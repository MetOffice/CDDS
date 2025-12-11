# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import configparser
import hashlib
import iris
import os
import subprocess

from collections import defaultdict
from datetime import datetime

from mip_convert.tests.test_functional.utils.constants import DEBUG, COMPARE_NETCDF, COMPARE_NETCDF_META


def quick_compare(outputs, hashes):
    """Performs a fast comparison of file contents using hashed data

    Parameters
    ----------
    outputs : List[str]
        The output files that should be compared to the reference files
    references : List[str]
        The references files compare to
    hashes : List[str]
        List of hashes

    Returns
    -------
    List[str]
        Corresponding compare commands
    """

    diffs = []
    for output, hash in zip(outputs, hashes):
        cl = iris.load(output)
        hashed_cubes = ''
        for cube in cl:
            hashed_cubes += hashlib.md5(cube.data).hexdigest()
        if hashed_cubes != hash:
            diffs.append('Output file {} hash ({}) differs from reference hash ({})'.format(
                output, hashed_cubes, hash
            ))
    msg = ', '.join(diffs)
    assert diffs == [], msg


def compare_command(outputs, references, tolerance_value=None, ignore_history=False, other_options=None):
    """Returns the compare commands for the given output files and their reference files

    Parameters
    ----------
    outputs : List[str]
        The output files that should be compared to the reference files
    references : List[str]
        The references files compare to
    tolerance_value : str
        Compare if absolute difference > tolerance value
    ignore_history : bool
        Compare global history attribute
    other_options : str
        Additional options for comparing

    Returns
    -------
    List[str]
        Corresponding compare commands
    """
    tolerance = '--tolerance={}'.format(tolerance_value) if tolerance_value else ''
    history = '--Attribute=history' if ignore_history else ''
    options = other_options if other_options else ''

    compare_commands = [
        COMPARE_NETCDF.format(tolerance=tolerance,
                              history=history,
                              options=options,
                              output=output,
                              reference=reference).split()
        for output, reference in zip(outputs, references)]

    return compare_commands


def compare(compare_commands):
    """Runs the given compare commands and returns if the result is that the
    compared files are equal or not.

    Parameters
    ----------
    compare_commands : List[str]
        Compare commands to run

    Returns
    -------
    bool, str
        Is equal or not and the message
    """
    differences = []
    nccmp_timings = []
    start_time = datetime.now()
    for command in compare_commands:
        print('Running compare command:', ' '.join(command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # The communicate() method returns a tuple in the form (stdoutdata, stderrdata).
        differences.append(process.communicate())

        # From the nccmp help: "Exit code 0 is returned for identical files,
        # 1 for different files, and 2 for a fatal error".
        # In addition, process.returncode = -11 when a segmentation fault occurs.
        if process.returncode < 0 or process.returncode == 2:
            raise AssertionError('Problem running comparison command: {}'.format(' '.join(command)))

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    nccmp_timings.append(elapsed_time.total_seconds())
    number_of_tests = 1  # len([test for test in dir() if test.startswith('test')])  # Refactor this one

    if len(nccmp_timings) == number_of_tests:
        print('nccmp took {:.3}s'.format(sum(nccmp_timings)))

    if DEBUG:
        stdoutdata = [output[0] for output in differences]
        print(stdoutdata)

    # If there are any differences, nccmp sends output to STDERR.
    stderrdata = [output[1] for output in differences]
    message = 'The following differences were present: {}'.format(set(stderrdata))
    assert set(stderrdata) == set(['']), message


def write_user_configuration_file(config_file_handle, test_data):
    """Write the test data into the given user configuration file

    Parameters
    ----------
    config_file_handle : TextIOWrapper
        User configuration file
    test_data : AbstractTestData
        Test data to be written into the configuration file
    """
    user_config = configparser.ConfigParser(interpolation=None)
    user_config.optionxform = str  # Preserve case.
    config = defaultdict(dict)
    all_info = test_data.as_list_dicts()

    for info in all_info:
        for section, items in info.items():
            config[section].update(items)

    user_config.update(config)
    with os.fdopen(config_file_handle, 'w') as file_handle:
        user_config.write(file_handle)


def print_outcome(outcome_files, output_directory, data_directory):
    """Prints if expected outcome files are correctly created

    Parameters
    ----------
    outcome_files : List[str]
        Outcome file paths that should be created
    output_directory : str
        Output directory that should contain the outcome files
    data_directory : str
        Data directory that should contain the cmor log file
    """
    for output_come_file in outcome_files:
        if not os.path.isfile(output_come_file):
            output_dir_contents = os.listdir(output_directory)
            if not output_dir_contents:
                print((
                    'Output file not created. Please check "{data_dir}/cmor.log"'.format(data_dir=data_directory)
                ))
            else:
                if len(output_dir_contents) == 1:
                    output_dir_contents = output_dir_contents[0]
                print((
                    'CMOR did not create the correctly named output file; output directory contains '
                    '"{output_dir_contents}"'.format(output_dir_contents=output_dir_contents)
                ))
