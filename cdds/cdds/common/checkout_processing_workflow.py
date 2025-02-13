# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.md for license details.

import argparse
import glob
import os
import shutil
from pathlib import Path
from typing import Union

from cdds import _NUMERICAL_VERSION
from cdds.common import determine_rose_suite_url
from cdds.common.constants import PROCESSING_WORKFLOW, WORKFLOWS_DIRECTORY
from cdds.common.request.request import read_request
from cdds.convert.process.workflow_interface import update_suite_conf_file


def main_checkout_workflow(arguments: Union[list, None] = None):
    """Main function for handling checking out the CDDS Processing Workflow to a specific
    location and updating relevant fields in the rose-suite.conf

    :param arguments: Optionally pass in a list of arguments for testing purposes.
    :type arguments: Union[list, None], optional
    :raises FileNotFoundError: Raised if the target directory doesn't exist.
    """

    args = parse_args(arguments)

    workflow_dst = Path(args.workflow_destination, args.workflow_name).expanduser()

    validate_arguments(args)
    export_processing_workflow(workflow_dst)
    update_rose_conf(args, workflow_dst)


def export_processing_workflow(destination):
    """
    Copy processing workflow to the destination folder.

    :param destination: Path to the destination folder
    :type destination: str
    """
    cwd = Path(__file__).parent.parent.resolve()
    source = os.path.join(cwd, WORKFLOWS_DIRECTORY, PROCESSING_WORKFLOW)

    shutil.copytree(source, destination, dirs_exist_ok=True)


def parse_user_input(workflow_dst: Path):
    """Handle user input for deletion of existing workflow.

    :param workflow_dst: Workflow destination
    :type workflow_dst: Path
    :raises EOFError:
    """
    usr_input = input("Delete files and overwrite existing workflow y/n?\n")

    if usr_input not in ["y", "n"]:
        print(f"{usr_input} is not a valid option. y/n")
        parse_user_input(workflow_dst)
    elif usr_input == "y":
        shutil.rmtree(workflow_dst)
        return None
    elif usr_input == "n":
        raise EOFError


def validate_arguments(args):
    """ Perform basic sanity checks on user inputs.

    :param args: User arguments from command line
    :type args: argparse.Namespace
    """
    if not Path(args.request_path).exists():
        raise RuntimeError(f"No request file at {args.request_path}")


def update_rose_conf(args, workflow_dst: Path):
    """Update the relevant fields of the copied suite with user provided arguments.

    :param args: User arguments from command line
    :type args: argparse.Namespace
    :param workflow_dst: Workflow destination
    :type workflow_dst: Path
    """

    conf_file = Path(workflow_dst, "rose-suite.conf")
    request_path = str(Path(args.request_path).expanduser().absolute())

    conf_override_fields = {
        "CDDS_VERSION": _NUMERICAL_VERSION,
    }
    print()
    print("Updating rose-suite.conf values.")

    changes = update_suite_conf_file(conf_file, "env", conf_override_fields, raw_value=True)
    print(changes)

    update_workflow_names(request_path, conf_file)


def get_request_files(request_location: str) -> list:
    """Return a list of the full paths of the request cfg files.

    :param request_location: Path to request file(s)
    :type request_location: str
    :raises IOError: If request_location is invalid.
    :raises IOError: If no request files are found.
    :rtype: list
    """
    if os.path.isfile(request_location):
        request_files = [request_location]
    elif os.path.isdir(request_location):
        glob_string = os.path.join(request_location, "*request*.cfg")
        request_files = glob.glob(glob_string)
    else:
        raise IOError(f"{request_location} is not a file/directory.")

    if not request_files:
        raise IOError(f"No request files matching the glob '*request*.cfg' were found in {request_location}")

    return request_files


def update_workflow_names(request_location: str, conf_file: Path) -> None:
    """ Populate the Jinja2 variables in the rose-suite.conf

    :param request_location: Path to request file(s)
    :type request_location: str
    :param conf_file: Path to rose-suite.conf
    :type conf_file: Path
    """
    request_files = get_request_files(request_location)

    workflow_names = []

    for request_file in request_files:
        request = read_request(request_file)
        workflow_names.append(("cdds_{}".format(request.common.workflow_basename),
                               request_file))

    conf_override_fields = {
        "WORKFLOW_NAMES": workflow_names,
    }

    changes = update_suite_conf_file(conf_file, "template variables", conf_override_fields, False)
    print(changes)


def parse_args(arguments: Union[list, None]) -> argparse.Namespace:
    """Configure the parser for providing commands

    :param arguments: Optionally pass in a list of arguments for testing purposes.
    :type arguments: Union[list, None], optional
    :return: The configured argpase object.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow_name", help="Desired workflow name")
    parser.add_argument(
        "request_path",
        default=None,
        help="Either, a path to a request.cfg file, or directory containing request*.cfg files.",
    )
    parser.add_argument(
        "--workflow_destination",
        default="~/roses",
        help="Specify destination directory. Default is ~/roses",
    )
    parsed_arguments = parser.parse_args(arguments)

    return parsed_arguments
