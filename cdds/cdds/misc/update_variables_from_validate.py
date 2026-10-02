#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""
This script removes variables from the variable list that have been identifies by extract validate as containing
STASH errors (typically due to missing STASH).This should be run after extract validate has completed with the example
command line usage of:

`update_variables_from_valdiate <request> --streams <streams>`

The log file produced with this script can be found in the $proc_dir/prepare/log.
"""
import argparse
import logging

from pathlib import Path

from cdds.common import configure_logger
from cdds.common.request.request import read_request, Request
from cdds.common.plugins.plugins import PluginStore


def get_logger(request: Request, plugin) -> logging.Logger:
    """Configures and set up the log name ready for use.

    Parameters
    ----------
    request: Request
        The request configuration file.
    plugin:
        The plugin.

    Returns
    -------
    logging.Logger
        The logger.
    """
    # Create the full log path and filename
    prepare_dir = Path(plugin.proc_directory(request)) / "prepare" / "log"
    if not Path.exists(prepare_dir):
        raise FileNotFoundError(f"Prepare directory: '{prepare_dir}' does not exist.")
    log_name = prepare_dir / f"update_variable_list_from_validate"

    configure_logger(str(log_name), "DEBUG", append_log=True)

    return logging.getLogger(__name__)


def arg_parser() -> argparse.Namespace:
    """Creates an argument parser to take user inputs from the command line.

    Returns
    -------
    argparse.Namespace
        The argument parser to handle source file paths.
    """
    parser = argparse.ArgumentParser(description=("This is a command line tool to append or remove an item from the "
                                                  "known_issues.json file."))
    parser.add_argument("request", help="The path to the request file.")
    parser.add_argument("-s", "--streams", nargs='*', help="The streams to ammend variables for. No specification will "
                        "process all streams listed in the request.")

    return parser.parse_args()


def check_log_type(plugin, request):
    """Checks whether any extract validate logs are present. If not, mip_convert logs are used."""
    extract_log_dir = Path(plugin.proc_directory(request)) / "extract" / "log"
    mip_convert_log_dir = Path(plugin.proc_directory(request)) / "convert" / "log"

    if list(extract_log_dir.glob("validate_*.log")):
        return extract_log_dir, "validate"

    elif list(mip_convert_log_dir.glob("**/mip_convert_*.log.gz")):
        return mip_convert_log_dir, "convert"


def get_log(root_log_type, root_log_dir, stream):
    logger = logging.getLogger(__name__)
    if root_log_type == "validate":
        search_regex = f"**/validate_{stream}*.log"
    elif root_log_type == "convert":
        search_regex = f"**/{stream}_*/mip_convert_*.log.gz"

    logs_for_stream = list(root_log_dir.glob(search_regex))
    if not logs_for_stream:
        logger.info(f"No {root_log_type} logs found. Skipping stream {stream}...")
        return ""

    # If there are more than one mip convert log files, find the most recent
    log = sorted(logs_for_stream)[-1]
    logger.info(f"Using most recent log file {log}")

    return log


def get_vars_to_remove(validate_log: Path) -> list:
    """Reads the variables that have been flagged as faulty for a single log file.

    Parameters
    ----------
    validate_log: Path
        The extract validate log file to read.

    Returns
    -------
    list
        The list of faulty variables to be commented out.
    """
    with open(validate_log, "r") as f:
        log = f.readlines()

    faulty_variable_flag = "As a result, these variables cannot be produced:"

    # If the faulty variable flag is not in the file, return an empty list (no variables to remove)
    if open(validate_log, 'r').read().find(faulty_variable_flag) == -1:
        return []
    else:
        for i, line in enumerate(log):
            # Identify the line containing the faulty variable flag and take the snippet of the log that comes after it.
            if faulty_variable_flag in line:
                log = log[i:]
                break
        # Reformat the log content to a list of variables.
        return format_to_list(log)


def format_to_list(log: list) -> list:
    """Formats the faulty variables in the extract validate log as a list, removing realm tags.

    Parameters
    ----------
    log: list
        A shortened snippet of the log file containing only the variables that have been flagged as faulty and their
        realm information.

    Returns
    -------
    list
        A list of variables to be removed.
    """
    variables = []
    # Remove any uneccesary realm information given in the log and any whitespace.
    for realm in log[1:-1]:
        variables += [item.strip() for item in realm.split(":")[-1].split(",")]

    return variables


def read_variable_list(variable_list_file: str) -> list:
    """Reads the variable list line by line into a list

    Parameters
    ----------
    variable_list_file: str
        The variable list file path from the request.

    Returns
    -------
    list
        The variable list file content as a list of lines.

    Raises
    ------
    RuntimeError
        If the variable list file is empty.
    """
    try:
        with open(variable_list_file, "r") as f:
            variable_list = [line.strip() for line in f]
    except FileNotFoundError:
        home_dir = Path.home()
        variable_list_file = variable_list_file.replace("~", str(home_dir))
        with open(variable_list_file, "r") as f:
            variable_list = [line.strip() for line in f]

    if not variable_list:
        raise RuntimeError(f"Variable list '{variable_list_file}' is empty, no starting variables found.")

    return variable_list


def save_new_variable_list(request: Request, updated_variable_list: list) -> None:
    """Saves the new variable list with commented out variable, overriding the old list.

    Parameters
    ----------
    request: Request
        The key information from the request configuration file.
    updated_variable_list: list
        The list of ammended lines for the variable list with faulty variables commented out. This will override the
        old variable list.
    """
    with open(request.data.variable_list_file, "w") as f:
        for line in updated_variable_list:
            f.write(f"{line}\n")


def main_update_variables_from_validate() -> None:
    """Main"""
    args = arg_parser()
    request = read_request(args.request)
    plugin = PluginStore.instance().get_plugin()

    logger = get_logger(request, plugin)

    variable_list = read_variable_list(request.data.variable_list_file)
    logger.info(f"Reading variable list file `{request.data.variable_list_file}`")

    streams = request.data.streams if not args.streams else args.streams
    root_log_path, root_log_type = check_log_type(plugin, request)
    count = 0
    for stream in streams:
        logger.info(f"Checking for faulty variables in stream {stream}")
        log = get_log(root_log_type, root_log_path, stream)
        if not log:
            continue
        # CONTINUE FROM HERE ------------------------------------------------------------------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        vars_to_remove = get_vars_to_remove(root_log_type, log)
        if vars_to_remove:
            logger.info(f"  Identified variables with stash errors in {stream}")
            # Itterate through the variable list line by line, if the variable in that line is also in the
            # vars_to_remove list, comment them out.
            for i, line in enumerate(variable_list):
                for variable in vars_to_remove:
                    if variable in line and stream in line and not line.startswith("#"):
                        variable_list[i] = f"#{line} #removed due to extract validation error"
                        logger.info(f"      Removed variable `{variable}`")
                        count += 1
        else:
            logger.info(f"  No variables with stash errors in {stream}")

    save_new_variable_list(request, variable_list)
    logger.info(f"Variable list {request.data.variable_list_file} successfully updated. Removed {count} variables.")
