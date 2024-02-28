# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import Union

from cdds import _NUMERICAL_VERSION
from cdds.arguments import read_default_arguments
from cdds.common.constants import PROCESSING_WORKFLOW
from cdds.common import determine_rose_suite_url
from cdds.convert.process.workflow_interface import (
    check_svn_location,
    checkout_url,
    update_suite_conf_file,
)


def main_checkout_workflow(arguments: Union[list, None] = None):
    """Main function for handling checking out the CDDS Processing Workflow to a specific
    location and updating relevant fields in the rose-suite.conf

    :param arguments: Optionally pass in a list of arguments for testing purposes.
    :type arguments: Union[list, None], optional
    :raises FileNotFoundError: Raised if the target directory doesn't exist.
    """

    args = parse_args(arguments)

    workflow_url = determine_rose_suite_url(PROCESSING_WORKFLOW, args.external_repository)
    workflow_url += args.branch_name

    workflow_dst = Path(args.workflow_destination, args.workflow_name).expanduser()

    validate_arguments(args, workflow_url)
    create_workflow_dst(workflow_dst)
    checkout_url(workflow_url, workflow_dst)
    update_rose_conf(args, workflow_dst)
    run_macros(workflow_dst)


def parse_user_input(workflow_dst: Path):
    """Handle user input for deletion of existing workflow.

    :param workflow_dst: Workflow destination
    :type workflow_dst: Path
    :raises EOFError:
    """
    usr_input = input(f"Delete files and overwrite existing workflow y/n?\n")

    if usr_input not in ["y", "n"]:
        print(f"{usr_input} is not a valid option. y/n")
        parse_user_input(workflow_dst)
    elif usr_input == "y":
        shutil.rmtree(workflow_dst)
        return None
    elif usr_input == "n":
        raise EOFError


def validate_arguments(args, workflow_url: str):
    """ Perform basic sanity checks on user inputs.

    :param args: User arguments from command line
    :type args: argparse.Namespace
    :param workflow_url: Workflow branch url
    :type workflow_url: str
    """

    if not check_svn_location(workflow_url):
        raise RuntimeError(f"No branch at {workflow_url}")
    if not Path(args.request_path).exists():
        raise RuntimeError(f"No request file at {args.request_path}")
    if not Path(args.variables_file).exists():
        raise RuntimeError(f"No variables file at {args.variables_file}")


def create_workflow_dst(workflow_dst: Path):
    """Check whether the existing directory already contains a workflow.

    :param workflow_dst: Workflow destination
    :type workflow_dst: Path
    """

    if not workflow_dst.is_dir():
        workflow_dst.mkdir(parents=True)

    elif not Path(workflow_dst / "flow.cylc").exists():
        msg = f"Target directory {workflow_dst} exists but is not a workflow. Aborting operation."
        raise RuntimeError(msg)

    elif Path(workflow_dst / "flow.cylc").exists():
        print(f"Target directory {workflow_dst} already contains a workflow.\n")
        for dirpath, _, filenames in os.walk(workflow_dst):
            if filenames:
                for file in filenames:
                    print("/".join([dirpath, file]))

        parse_user_input(workflow_dst)

    else:
        raise RuntimeError(f"Could not create {workflow_dst}")


def update_rose_conf(args, workflow_dst: Path):
    """Update the relevant fields of the copied suite with user provided arguments.

    :param args: User arguments from command line
    :type args: argparse.Namespace
    :param workflow_dst: Workflow destination
    :type workflow_dst: Path
    """

    conf_file = Path(workflow_dst, "rose-suite.conf")
    request_path = str(Path(args.request_path).expanduser().absolute())
    variables_path = str(Path(args.variables_file).expanduser().absolute())

    conf_override_fields = [
        ("REQUEST_CONFIG_PATH", request_path, "env", True),
        ("USER_VARIABLES_LIST", variables_path, "env", True),
        ("CDDS_VERSION", _NUMERICAL_VERSION, "env", True),
    ]
    print()
    print("Updating rose-suite.conf values.")
    for key, value, section_name, raw_value in conf_override_fields:
        changes_to_apply = {key: value}
        changes = update_suite_conf_file(conf_file, section_name, changes_to_apply, raw_value)
        print(changes)


def run_macros(workflow_dst: Path):
    """Run the rose macros used for populating the STREAMS and WORKFLOW_NAMES jinja2 variable values.

    :param workflow_dst: Workflow destination
    :type workflow_dst: Path
    """
    macro_cmd_streams = f"rose macro load_streams.LoadStreams --suite-only -y -C {workflow_dst}"
    macro_cmd_workflows = f"rose macro generate_workflow_names.GenerateWorkflowNames --suite-only -y -C {workflow_dst}"
    print()
    print("Running rose macros.")
    for macro_cmd in [macro_cmd_streams, macro_cmd_workflows]:
        cmd = macro_cmd.split()
        completed_process = subprocess.run(cmd, capture_output=True, encoding="utf-8")
        print(completed_process.stdout)
        # needed due to a quirk of using "rose macro" via cmd line which outputs a rose-app.conf
        Path(workflow_dst / "rose-app.conf").replace(Path(workflow_dst / "rose-suite.conf"))


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
        help="Use external repository (https://code.metoffice.gov.uk/svn/roses-u) "
             "instead of internal mirror (svn://fcm1/roses-u.xm_svn)"
    )
    parsed_arguments = parser.parse_args(arguments)

    return parsed_arguments
