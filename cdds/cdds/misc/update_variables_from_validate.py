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
import os

from pathlib import Path

from cdds.common import configure_logger
from cdds.common.request.request import read_request, Request


def get_logger(request: Request) -> logging.Logger:
    """Configures and set up the log name ready for use.

    Parameters
    ----------
    request: Request
        The request configuration file.

    Returns
    -------
    logging.Logger
        The logger.
    """
    # Create the full log path and filename
    prepare_dir = generate_full_procdir(request) / "prepare" / "log"
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


def generate_full_procdir(request: Request) -> Path:
    """Generates the full path to the proc directory using key information from the request.

    Parameters
    ----------
    request: Request
        The key information from the request configuration file.

    Returns
    -------
    Path
        The full path to the proc directory using key information from the request.
    """
    log_dir = (Path(request.common.root_proc_dir) / request.metadata.mip_era / request.metadata.mip /
               f"{request.metadata.model_id}_{request.metadata.experiment_id}_{request.metadata.variant_label}" /
                 request.common.package)

    return log_dir


def get_newest_validate_log(logs_for_stream: list):
    """Identifies the most recent log from the list of given log files for a single stream.

    Parameters
    ----------
    logs_for_stream: list
        All logs currently available for a single stream.

    Returns
    -------
    :
        The path of the most recent extract validate log file or an empty string if no log file is found.
    """
    logger = logging.getLogger(__name__)
    # If there are more than one extract validate log files find the most recent
    if not logs_for_stream:
        logger.info("No extract validate log found. Skipping stream...")
        return ""

    elif len(logs_for_stream) > 1:
        # Get a list of all of the datetimes referenced in the extract validate log file names. Find the most recent and
        # identify the log file it belongs to.
        datetimes = [log.split("_")[-1].split(".")[0] for log in logs_for_stream]
        latest = max(datetimes)
        for log in logs_for_stream:
            if latest in log:
                log = log
    # If there is only one extract validate log file for the given stream, use that one.
    else:
        log = logs_for_stream[0]

    logger.info(f"Using most recent log file {log}")

    return log


def get_validate_log(log_dir: Path, stream: str):
    """Identify the extract validate log to read for a single stream.

    Parameters
    ----------
    log_dir: Path
        The log containing all extract validate logs.
    stream: str
        The stream whos extract validate log is being checked.

    Returns
    -------
    :
        The path to the latest validate log file for a single stream or an empty string if none exists.
    """
    logs_for_stream = []
    for (root, dirs, files) in os.walk(log_dir):
        for file in files:
            if f"validate_{stream}" in file:
                logs_for_stream.append(file)

    # Identify the most recent log for that stream.
    validate_log = get_newest_validate_log(logs_for_stream)
    if not validate_log:
        return ""

    return Path(log_dir) / validate_log


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
    logger = get_logger(request)

    variable_list = read_variable_list(request.data.variable_list_file)
    logger.info(f"Reading variable list file `{request.data.variable_list_file}`")

    streams = request.data.streams if not args.streams else args.streams
    extract_log_dir = generate_full_procdir(request) / "extract" / "log"
    count = 0
    for stream in streams:
        logger.info(f"Checking for faulty variables in stream {stream}")
        validate_log = get_validate_log(extract_log_dir, stream)
        if not validate_log:
            continue
        vars_to_remove = get_vars_to_remove(validate_log)
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
