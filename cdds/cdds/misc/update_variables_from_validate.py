#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""
This script removes variables from the variable list that have been identifies by extract validate as containing
STASH errors (typically due to missing STASH).This should be run after extract validate has completed with the example
command line usage of:

`update_variables_from_valdiate <request> --streams <streams>`

Updated as of 05/10/2026: This script can now also remove variables using mip_convert logs. It will pick up the most
recent log from each substream (e.g. `mip_convert_ap6_latlon-native`, `mip_convert_ap6_uvgrid` will each have a single
log file searched for faulty variables).

The log file produced with this script can be found in the $proc_dir/prepare/log.
"""
import argparse
import logging
import gzip

from pathlib import Path

from cdds.common import configure_logger
from cdds.common.request.request import read_request, Request
from cdds.common.plugins.plugins import PluginStore, CddsPlugin


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
    parser.add_argument("-s", "--streams", nargs='*', help="The streams to amend variables for. No specification will "
                        "process all streams listed in the request.")

    return parser.parse_args()


def check_log_type(plugin: CddsPlugin, request: Request) -> tuple[Path, str]:
    """Checks whether any extract validate logs are present. If not, mip_convert logs are used. Returns the appropriate
    directory and a note of the type of log used for easy separation of handling.

    Parameters
    ----------
    plugin: CddsPlugin
        The CDDS plugin.
    request: Request
        The CDDS request file.

    returns
    -------
    tuple[Path, str]
        The path to the log file directory being read and the type of log being looked at ('validate' or 'convert').
    """
    extract_log_dir = Path(plugin.proc_directory(request)) / "extract" / "log"
    mip_convert_log_dir = Path(plugin.proc_directory(request)) / "convert" / "log"

    if list(extract_log_dir.glob("validate_*.log")):
        return extract_log_dir, "validate"

    elif list(mip_convert_log_dir.glob("**/mip_convert_*.log.gz")):
        return mip_convert_log_dir, "convert"

    else:
        raise RuntimeError("No convert or validate log files found.")


def get_log(root_log_type: str, root_log_dir: Path, stream: str) -> list:
    """Returns the most recent log file(s) associated with a given stream. When using mip convert logs, multiple logs
    may be identified is multiple sub streams are being processed.

    Parameters
    ----------
    root_log_type: str
        'validate' or 'convert', the type of log file being read. These highlight variables that cannot be produced with
        different formatting and different verbiage, hence must be handled separately.
    root_log_dir: Path
        The path to the log file directory being read.
    stream: str
        The stream being processed.

    Returns
    -------
    list
        The list of paths to the most recent log file(s) for a given stream.
    """
    logger = logging.getLogger(__name__)
    logs = []
    if root_log_type == "validate":
        search_regex = f"**/validate_{stream}*.log"
        logs_for_stream = list(root_log_dir.glob(search_regex))
        logs.append(sorted(logs_for_stream, key=sort_by_filename_only)[-1])
    elif root_log_type == "convert":
        search_regex = f"**/mip_convert_*.log.gz"
        # Check the convert sub directories for sub streams i.e. latlon-native, u-grid, v-grid etc, we need the latest
        # log from each of these.
        for directory in root_log_dir.glob("*/"):
            if stream in str(directory):
                # Conduct a full file search only under the directories associated with the given stream.
                logs_for_stream = list(directory.glob(search_regex))
                logs.append(sorted(logs_for_stream, key=sort_by_filename_only)[-1])

    if not logs:
        logger.info(f"No {root_log_type} log(s) found. Skipping stream {stream}...")
    else:
        logger.info(f"Using most recent log(s) file {logs}")

    return logs


def sort_by_filename_only(log):
    """Ensures file paths are sorted according to the filename only and not any subdirectories to ensure only the most
    recent logs are checked."""
    return str(log).split("/")[-1]


def get_vars_to_remove(root_log_type: str, logs: list[Path]) -> list[str]:
    """Reads the variables that have been flagged as faulty for a single log file.

    Parameters
    ----------
    root_log_type: str
        'validate' or 'convert', the type of log file being read. These highlight variables that cannot be produced with
        different formatting and different verbiage, hence must be handled separately.
    logs: list[Path]
        The list of paths to the logfiles being read.

    Returns
    -------
    list[str]
        The list of faulty variables to be commented out.
    """
    if root_log_type == "validate":
        faulty_variable_flag = 'As a result, these variables cannot be produced:'
    elif root_log_type == "convert":
        faulty_variable_flag = 'No cubes found using constraints "lbuser4='

    log_lines = read_log_content(root_log_type, logs)
    if root_log_type == "validate":
        vars_to_remove = grep_validate_log(faulty_variable_flag, log_lines)
    elif root_log_type == "convert":
        vars_to_remove = grep_convert_log(faulty_variable_flag, log_lines)

    return vars_to_remove


def read_log_content(root_log_type: str, logs: list[Path]) -> list[str]:
    """Reads a single log file.

    Parameters
    ----------
    root_log_type: str
        'validate' or 'convert', the type of log file being read. These highlight variables that cannot be produced with
        different formatting and different verbiage, hence must be handled separately.
    logs: list[Path]
        The list of paths to the logfile being read.

    Returns
    -------
    list[str]
        The combined content of the log file(s) as a list of lines.
    """
    log_lines = []
    for log in logs:
        if root_log_type == "validate":
            with open(log, "r") as f:
                log_lines += f.readlines()
        # Mip convert logs are gzipped, these need to be opened differently from standard txt logs
        elif root_log_type == "convert":
            with gzip.open(log, "rt") as f:
                log_lines += f.readlines()

    return log_lines


def grep_validate_log(faulty_variable_flag: str, log_lines: list[str]) -> list[str]:
    """Greps through a single validate log to identify any variables that have been noted as unproducible. Variables are
    listed at the base of the file after the faulty variable flag.

    Parameters
    ----------
    faulty_variable_flag: str
        The string used in the log file to signify that the following variable(s) is unproducible.
    log_lines: list[str]
        The content of the log file as a list of lines.

    Returns
    -------
    list[str]
        The list of variables that cannot be produced and need to be removed from the variable list.
    """
    for i, line in enumerate(log_lines):
        # Identify the line containing the faulty variable flag and take the snippet of the log that comes after it.
        if faulty_variable_flag in line:
            truncated_log = log_lines[i:]
            break
    # Reformat the log content to a list of variables.
    return format_to_list(truncated_log)


def grep_convert_log(faulty_variable_flag: str, log_lines: list[str]) -> list[str]:
    """Greps through a single validate log to identify any variables that have been noted as unproducible. Variables are
    noted inline with the faulty variable flag.

    Parameters
    ----------
    faulty_variable_flag: str
        The string used in the log file to signify that the following variable(s) is unproducible.
    log_lines: list[str]
        The content of the log file as a list of lines.

    Returns
    -------
    list[str]
        The list of variables that cannot be produced and need to be removed from the variable list.
    """
    faulty_variables = []
    for line in log_lines:
        if faulty_variable_flag in line:
            faulty_variables.append(line.split('"')[1])

    return faulty_variables


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
    # Remove any unnecessary realm information given in the log and any whitespace.
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
        # Pathlib interprets '~' as literal rather than $HOME, attempt to interpret any instance of this manually if the
        # given path cannot be found.
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
        The list of amended lines for the variable list with faulty variables commented out. This will override the
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
        logs = get_log(root_log_type, root_log_path, stream)
        if not logs:
            continue
        vars_to_remove = get_vars_to_remove(root_log_type, logs)
        if vars_to_remove:
            logger.info(f"  Identified variables with stash errors in {stream}")
            # Iterate through the variable list line by line, if the variable in that line is also in the
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
