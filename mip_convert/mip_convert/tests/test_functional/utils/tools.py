# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import configparser
import hashlib
import os
import subprocess

from collections import defaultdict
from datetime import datetime

from mip_convert.tests.test_functional.utils.constants import DEBUG, COMPARE_NETCDF, COMPARE_NETCDF_META


def quick_compare(outputs, references):
    """
    Performs a fast comparison of file metadata and file size for the given output files and their reference files

    :param outputs: The output files that should be compared to the reference files
    :type outputs: List[str]
    :param references: The references files compare to
    :type references: List[str]
    :return: Corresponding compare commands
    :rtype: List[str]
    """

    compare_commands = [
        COMPARE_NETCDF_META.format(output=output, reference=reference).split()
        for output, reference in zip(outputs, references)]
    compare(compare_commands)
    diffs = []
    for output, reference in zip(outputs, references):
        output_size = os.path.getsize(output)
        reference_size = os.path.getsize(reference)
        if output_size != reference_size:
            diffs.append('Output file {} size ({}) differs from reference file {} size ({})'.format(
                output, output_size, reference, reference_size
            ))
    msg = ', '.join(diffs)
    assert diffs == [], msg


def compare_command(outputs, references, tolerance_value=None, ignore_history=False, other_options=None):
    """
    Returns the compare commands for the given output files and their reference files

    :param outputs: The output files that should be compared to the reference files
    :type outputs: List[str]
    :param references: The references files compare to
    :type references: List[str]
    :param tolerance_value: Compare if absolute difference > tolerance value
    :type tolerance_value: str
    :param ignore_history: Compare global history attribute
    :type ignore_history: bool
    :param other_options: Additional options for comparing
    :type other_options: str
    :return: Corresponding compare commands
    :rtype: List[str]
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
    """
    Runs the given compare commands and returns if the result is that the
    compared files are equal or not.

    :param compare_commands: Compare commands to run
    :type compare_commands: List[str]
    :return: Is equal or not and the message
    :rtype: bool, str
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
    """
    Write the test data into the given user configuration file

    :param config_file_handle: User configuration file
    :type config_file_handle: TextIOWrapper
    :param test_data: Test data to be written into the configuration file
    :type test_data: AbstractTestData
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
    """
    Prints if expected outcome files are correctly created

    :param outcome_files: Outcome file paths that should be created
    :type outcome_files: List[str]
    :param output_directory: Output directory that should contain the outcome files
    :type output_directory: str
    :param data_directory: Data directory that should contain the cmor log file
    :type data_directory: str
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
