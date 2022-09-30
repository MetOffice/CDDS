# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.

import os

from cdds.tests.nightly_tests.setup_task.arguments import parse_arguments
from cdds.tests.nightly_tests.setup_task.activities import (setup_directory_structure, setup_mass_directories,
                                                            create_variable_list, link_input_data)
from cdds.common import configure_logger
from cdds.deprecated.config import FullPaths
from cdds.common.request import read_request


def main():
    arguments = parse_arguments()
    request_json_path = arguments.request_json_path
    request = read_request(request_json_path)
    full_paths = FullPaths(arguments, request)
    configure_logger('cdds_setup.log', arguments.log_level, False)

    setup_directory_structure(arguments, request)
    setup_mass_directories(arguments)

    # creating symlinks from the test directory to the data and proc directories on /project
    os.symlink(full_paths.data_directory, os.path.join(arguments.test_dir, '{0}_data'.format(request.package)))
    os.symlink(full_paths.proc_directory, os.path.join(arguments.test_dir, '{0}_proc'.format(request.package)))

    create_variable_list(arguments)
    link_input_data(arguments, full_paths)
