# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Union

from cdds.arguments import read_default_arguments
from cdds.common.constants import PROCESSING_WORKFLOW
from cdds.common.request import read_request
from cdds.common import determine_rose_suite_url
from cdds.convert.process.workflow_interface import (
    check_svn_location,
    checkout_url,
    update_suite_conf_file,
)


def main_checkout_workflow(arguments: Union[list, None] = None):
    """Main function for handling checking out the CDDS Processing Suite to a specific
    location and updating relevant fields in the rose-suite.conf

    :param arguments: Optionally pass in a list of arguments for testing purposes.
    :type arguments: Union[list, None], optional
    :raises FileNotFoundError: Raised if the target directory doesn't exist.
    """

    args = parse_args(arguments)

    workflow_url = determine_rose_suite_url(PROCESSING_WORKFLOW, args.external_repository)
    workflow_url += args.branch_name

    dst_directory = os.path.expanduser(args.workflow_destination)
    dst_directory = Path(dst_directory, args.workflow_name)

    if not Path(dst_directory).is_dir():
        Path(dst_directory).mkdir(parents=True)
    elif Path(dst_directory).is_dir():
        existing_dir(dst_directory)
    else:
        raise FileNotFoundError("Could not determine the workflow target directory.")

    if check_svn_location(workflow_url):
        checkout_url(workflow_url, dst_directory)

    update_rose_conf(args, dst_directory)


def parse_usr_input(workflow_dst):
    usr_input = input(f"Delete files these files and overwrite existing workflow y/n?\n")

    if usr_input not in ["y", "n"]:
        print(f"{usr_input} is not a valid option. y/n")
        parse_usr_input(workflow_dst)
    elif usr_input == "y":
        shutil.rmtree(workflow_dst)
        return None
    elif usr_input == "n":
        raise EOFError


def existing_dir(workflow_dst):
    if not Path(workflow_dst / "flow.cylc").exists():
        print(
            "The target directory already exists but does not contain a workflow. Aborting operation."
        )

        sys.exit(1)

    if Path(workflow_dst / "flow.cylc").exists():
        print(f"The target directory {workflow_dst} already contains a workflow.\n")
        for a, _, c in os.walk(workflow_dst):
            if c:
                for file in c:
                    print("/".join([a, file]))

        parse_usr_input(workflow_dst)


def update_rose_conf(args, suite_directory: str):
    """Update the relevant fields of the copied suite with user provided arguments.

    :param args: User arguments from command line
    :type args: argparse.Namespace
    :param suite_directory: Directory of the copied suite.
    :type suite_directory: str
    """
    conf_file = os.path.join(suite_directory, "rose-suite.conf")
    conf_override_fields = [
        ("request_path", "REQUEST_JSON_PATH", "env", True),
        ("variables_file", "USER_VARIABLES_LIST", "template variables", True),
    ]

    for option, mapping, section_name, raw_value in conf_override_fields:
        if vars(args)[option]:
            if option in ["request_path", "variables_file"]:
                full_path = str(Path(vars(args)[option]).expanduser().absolute())
                changes_to_apply = {mapping: full_path}
            else:
                changes_to_apply = {mapping: vars(args)[option]}
            update_suite_conf_file(conf_file, section_name, changes_to_apply, raw_value)

    run_macros(suite_directory)


def run_macros(workflow_dst):
    macro_cmd_streams = f"rose macro load_streams.LoadStreams --suite-only -y -C {workflow_dst}"
    macro_cmd_workflows = f"rose macro generate_workflow_names.GenerateWorkflowNames --suite-only -y -C {workflow_dst}"

    for macro_cmd in [macro_cmd_streams, macro_cmd_workflows]:
        subprocess.run(macro_cmd.split())
        Path(workflow_dst / 'rose-app.conf').replace(Path(workflow_dst / 'rose-suite.conf'))


def parse_args(arguments: Union[list, None]) -> argparse.Namespace:
    """Configure the parser for providing commands

    :param arguments: Optionally pass in a list of arguments for testing purposes.
    :type arguments: Union[list, None], optional
    :return: The configured argpase object.
    :rtype: argparse.Namespace
    """
    default_arguments = read_default_arguments("cdds", "checkout_processing_workflow")

    parser = argparse.ArgumentParser()
    parser.add_argument("workflow_name", help="Desired workflow name")
    parser.add_argument(
        "request_path",
        default=None,
        help="Either, a path to a request.json file, or directory containing request*.json files",
    )
    parser.add_argument(
        "variables_file",
        default=None,
        help="The user variables file",
    )
    parser.add_argument(
        "--branch_name",
        default=default_arguments.processing_workflow_branch,
        help="Use an alternative branch.",
    )
    parser.add_argument(
        "--workflow_destination",
        default="~/roses",
        help="Specify destination directory. Default is ~/roses",
    )
    parser.add_argument(
        "--external_repository",
        action="store_false",
        help="Don't use external repository",
    )
    parsed_arguments = parser.parse_args(arguments)

    return parsed_arguments
