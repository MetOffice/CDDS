# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.

import argparse
import os
from typing import Union

from cdds.common import determine_rose_suite_url
from cdds.convert.process.suite_interface import (check_svn_location,
                                                  checkout_url,
                                                  update_suite_conf_file)


def main_checkout_suite(arguments: Union[list, None] = None):
    """Main function for handling checking out the CDDS Processing Suite to a specific
    location and updating relevant fields in the rose-suite.conf

    :param arguments: Optionally pass in a list of arguments for testing purposes.
    :type arguments: Union[list, None], optional
    :raises FileNotFoundError: Raised if the target directory doesn't exist.
    """

    args = parse_args(arguments)

    suite_url = determine_rose_suite_url("u-cq805", args.external_repository)
    suite_url += args.branch_name

    roses_directory = os.path.expanduser("~/roses/")

    if os.path.isdir(roses_directory) and not args.suite_destination:
        suite_directory = os.path.join(roses_directory, args.suite_name)
        os.mkdir(suite_directory)
    elif args.suite_destination:
        suite_directory = os.path.join(args.suite_destination, args.suite_name)
        os.makedirs(suite_directory)
    else:
        raise FileNotFoundError("Could not determine target directory.")

    if check_svn_location(suite_url):
        checkout_url(suite_url, suite_directory)

    update_rose_conf(args, suite_directory)


def update_rose_conf(args, suite_directory: str):
    """Update the relevant fields of the copied suite with user provided arguments.

    :param args: User arguments from command line
    :type args: argparse.Namespace
    :param suite_directory: Directory of the copied suite.
    :type suite_directory: str
    """
    conf_file = os.path.join(suite_directory, "rose-suite.conf")
    conf_override_fields = [("request_file", "REQUEST_JSON_PATH", "env", True),
                            ("variables_file", "USER_VARIABLES_LIST", "env", True),
                            ("suite_base_name", "SUITE_BASE_NAME", "jinja2:suite.rc", False)]
    for option, mapping, section_name, raw_value in conf_override_fields:
        if vars(args)[option]:
            changes_to_apply = {mapping: vars(args)[option]}
            update_suite_conf_file(conf_file, section_name, changes_to_apply, raw_value)


def parse_args(arguments: Union[list, None]) -> argparse.Namespace:
    """Configure the parser for providing commands

    :param arguments: Optionally pass in a list of arguments for testing purposes.
    :type arguments: Union[list, bool], optional
    :return: The configured argpase object.
    :rtype: argparse.Namespace
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('suite_name', help='The desired suite name.')
    parser.add_argument('--branch_name', default="trunk", help='The branch name. Uses trunk by default.')
    parser.add_argument('--request_file', default=None)
    parser.add_argument('--variables_file', default=None)
    parser.add_argument('--suite_base_name', default=None)
    parser.add_argument('--suite_destination', default=None, help='Destination directory to copy u-cq805 into.')
    parser.add_argument('--external_repository', action="store_false")
    parsed_arguments = parser.parse_args(arguments)

    return parsed_arguments
