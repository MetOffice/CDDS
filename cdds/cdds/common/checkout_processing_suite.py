# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.

import argparse
import json
import os
from configparser import ConfigParser

from cdds.convert.exceptions import SuiteConfigMissingValueError
from cdds.convert.process.suite_interface import (check_svn_location,
                                                  checkout_url,
                                                  update_suite_conf_file)


def main_checkout_suite():

    args = parse_args()

    suite_url = "svn://fcm1/roses-u.xm_svn/c/q/8/0/5/{}".format(args.branch_name)
    roses_directory = os.path.expanduser("~/roses/")

    if os.path.isdir(roses_directory) and not args.suite_destination:
        suite_directory = os.path.join(roses_directory, args.suite_name)
        os.mkdir(suite_directory)
    elif args.suite_destination:
        suite_directory = os.path.join(args.suite_destination, args.suite_name)
        os.makedirs(suite_directory)
    else:
        raise BaseException

    if check_svn_location(suite_url):
        checkout_url(suite_url, suite_directory)

    update_rose_conf(args, suite_directory)


def update_rose_conf(args, suite_directory):
    """Update the relevant fields of the copied suite with user provided arguments.

    :param args: User arguments from command line
    :type args: argparse.Namespace
    :param suite_directory: Directory of the copied suite.
    :type suite_directory: str
    """
    conf_file = os.path.join(suite_directory, "rose-suite.conf")
    conf_override_fields = [("request_file", "REQUEST_JSON_PATH", "env"),
                            ("variables_file", "USER_VARIABLES_LIST", "env"),
                            ("suite_base_name", "SUITE_BASE_NAME", "jinja2:suite.rc")]
    for option, mapping, section_name in conf_override_fields:
        if vars(args)[option]:
            if section_name == "jinja2:suite.rc":
                changes_to_apply = {mapping: json.dumps(vars(args)[option])}
            else:
                changes_to_apply = {mapping: vars(args)[option]}
            update_suite_conf_file(conf_file, section_name, changes_to_apply)


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('suite_name', help='The desired suite name.')
    args.add_argument('--branch_name', default="trunk", help='The branch name. Uses trunk by default.')
    args.add_argument('--request_file', default=None)
    args.add_argument('--variables_file', default=None)
    args.add_argument('--suite_base_name', default=None)
    args.add_argument('--suite_destination', default=None, help='Destination directory to copy u-cq805 into.')
    arguments = args.parse_args()

    return arguments
