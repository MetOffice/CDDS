# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import subprocess
import configparser
import os

from collections import defaultdict
from datetime import datetime

from mip_convert.tests.test_functional.utils.configurations import SpecificInfo, AbstractTestData
from mip_convert.tests.test_functional.utils.constants import DEBUG, NCCMP_TIMINGS, COMPARE_NETCDF


def compare_command(outputs, references, tolerance_value=None, ignore_history=False, other_options=None):
    tolerance = ''
    if tolerance_value is not None:
        tolerance = '--tolerance={tolerance_value}'.format(tolerance_value=tolerance_value)

    history = ''
    if ignore_history:
        history = '--Attribute=history'

    options = ''
    if other_options is not None:
        options = other_options

    compare_commands = [
        COMPARE_NETCDF.format(tolerance=tolerance,
                              history=history,
                              options=options,
                              output=output,
                              reference=reference).split()
        for output, reference in zip(outputs, references)]

    return compare_commands


def compare(compare_commands):
    differences = []
    start_time = datetime.now()
    for compare_command in compare_commands:
        print('Running compare command:', ' '.join(compare_command))
        process = subprocess.Popen(compare_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True)

        # The communicate() method returns a tuple in the form (stdoutdata, stderrdata).
        differences.append(process.communicate())

        # From the nccmp help: "Exit code 0 is returned for identical files,
        # 1 for different files, and 2 for a fatal error".
        # In addition, process.returncode = -11 when a segmentation fault occurs.
        if process.returncode < 0 or process.returncode == 2:
            message = 'Problem running comparison command: {compare_command}'
            raise AssertionError(message.format(compare_command=' '.join(compare_command)))

    end_time = datetime.now()
    duration = end_time - start_time
    NCCMP_TIMINGS.append(duration.total_seconds())
    number_of_tests = 1  # len([test for test in dir() if test.startswith('test')])  # Refactor this one

    if len(NCCMP_TIMINGS) == number_of_tests:
        print('nccmp took {:.3}s'.format(sum(NCCMP_TIMINGS)))
    if DEBUG:
        stdoutdata = [output[0] for output in differences]
        print(stdoutdata)

    # If there are any differences, nccmp sends output to STDERR.
    stderrdata = [output[1] for output in differences]
    message = 'The following differences were present: {}'.format(set(stderrdata))
    assert set(stderrdata) == set(['']), message


def write_user_configuration_file(os_handle, test_data: AbstractTestData):
    user_config = configparser.ConfigParser(interpolation=None)
    user_config.optionxform = str  # Preserve case.
    config = defaultdict(dict)
    all_info = test_data.as_list_dicts()
    for info in all_info:
        for section, items in info.items():
            config[section].update(items)

    user_config.update(config)
    with os.fdopen(os_handle, 'w') as file_handle:
        user_config.write(file_handle)


def print_outcome(outputs, output_directory, data_directory):
    for output in outputs:
        if not os.path.isfile(output):
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
