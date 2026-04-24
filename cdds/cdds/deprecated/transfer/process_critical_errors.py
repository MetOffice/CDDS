# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""
Package to process the critical log files produced on a stream by stream basis in mip convert and summarise the contents
of this file which is then printed back to the user within the ,main workflow in a step called `run_critical_check`.
"""

import os
import gzip
from pathlib import Path
from typing import Iterator


def read_critical_log_file(cdds_convert_proc_dir: str, stream: str) -> list:
    """Reads a single critical log file and returns the contents where each line is an item in a list.

    Parameters
    ----------
    cdds_convert_proc_dir: str
        The path to the cdds convert proc directory.
    stream: str
        The stream being processed.

    Returns
    -------
    list:
        The content of the critical issues file for the given stream where each line is a new item in the list.
    """
    logfile = os.path.join(cdds_convert_proc_dir, "log", f'critical_issues_{stream}.log')
    with open(logfile, "r") as critical_logs:
        critical_issues = critical_logs.readlines()

    return critical_issues


def process_critical_issues(critical_issues: list) -> list:
    """Process each line of the critical issues list to contain only the necessary information.

    Parameters
    ----------
    critical_issues: list
        The content of the critical issues file where each line is an item in the list.

    Returns
    -------
    list
        A list of only the key information of each issue in the critical issues file.
    """
    critical_issues_key_info = []
    for line in critical_issues:
        grid, timestamp, round, mip_log_file, error_msg = line.split("|")
        info = "".join(error_msg.split(":")[3:])
        variable = info.split('"')[1]
        realm = info.split('"')[3]
        msg = '"'.join(info.split('"')[4:])

        critical_issues_key_info.append(f"{grid}|{timestamp}|{mip_log_file}|{variable}|{realm}|{msg.strip()}")

    return critical_issues_key_info


def get_cmor_log_file_location(issue: str, cdds_convert_proc_dir: str) -> Path:
    """Returns the location of the cmor log file.

    Parameters
    ----------
    issue: str
        The key information about a single critical issue.
    cdds_convert_proc_dir: str
        The path to the cdds convert proc directory.

    Returns
    -------
    Path
        The path to the cmor log file for a given cycle point(timestamp).
    """
    grid, timestamp, mip_log_file, _, _, _ = issue.split("|")
    subdir = "_".join(grid.split("_")[2:]).strip("first_")
    cmor_log_filename = f'{mip_log_file.replace("mip_convert_", "cmor.")}.gz'
    cmor_log_file_location = Path(cdds_convert_proc_dir) / "log" / subdir / timestamp / "cmor_logs" / cmor_log_filename

    return cmor_log_file_location


def _summarise_cmor_error(line, cmor_logs, flag, variable, prefix):
    """Uses the defined flag and prefix to summarise the cmor error for the given variable.

    Parameters
    ----------
    line: str
        The current line in the cmor logs that is being read.
    cmor_logs: Iterator
        The full content of the cmor logs as an iterator.
    flag: str
        The error or warning statement used to differentiate general cmor log info from a specific error or warning.
        This is typically as simple as 'Error' or 'Warning'.
    variable: str
        The variable being processed.
    prefix: str
        The string prepended to the summarised issue to identify the type of cmor error (e.g. 'Problem with
        cmor_write_var_to_file')

    Returns
    -------
    str
        Summarised cmor error.
    """
    snippet = [line, [next(cmor_logs) for i in range(6)]]
    for text in snippet:
        if flag in text and variable in text:
            return prefix + ": " + text[:200].strip("! Error: ") + "..."


def check_issues_in_cmor_write(msg: str, cmor_logs: Iterator, variable: str) -> str:
    """Checks the cmor log file for any additional information on cmor.write errors for a single critical issue.

    Parameters
    ----------
    msg: str
        The current error message.
    cmor_logs: Iterator
        The content of the cmor log file as an iterator.
    variable: str
        The variable associated with the error.


    Returns
    -------
    str
        The error message updated with additional info from the cmor file.
    """
    for line in cmor_logs:
        if "cmor_write_var_to_file" in line:
            return _summarise_cmor_error(line, cmor_logs, "Error", variable, "Problem with cmor_write_var_to_file")

    return msg


def check_issues_in_cmor_variable(msg: str, cmor_logs: Iterator, variable: str) -> str:
    """Checks the cmor log file for any additional information on cmor.variable errors for a single critical issue.

    Parameters
    ----------
    msg: str
        The current error message.
    cmor_logs: Iterator
        The content of the cmor log file as an iterator.
    variable: str
        The variable associated with the error.

    Returns
    -------
    str
        The error message updated with additional info from the cmor file.
    """
    for line in cmor_logs:
        if "cmor_variable" in line:
            return _summarise_cmor_error(line, cmor_logs, "Error", variable, "Problem with cmor_variable")

    return msg


def check_issues_in_cmor_zfactor(msg: str, cmor_logs: Iterator, variable: str) -> str:
    """Checks the cmor log file for any additional information on cmor.zfactor errors for a single critical issue.

    Parameters
    ----------
    msg: str
        The current error message.
    cmor_logs: Iterator
        The content of the cmor log file as an iterator.
    variable: str
        The variable associated with the error.

    Returns
    -------
    str
        The error message updated with additional info from the cmor file.
    """
    for line in cmor_logs:
        if "cmor_zfactor" in line:
            return _summarise_cmor_error(line, cmor_logs, "Warning", variable, "Problem with cmor_zfactor")

    return msg


def check_issues_in_cmor_axis(msg: str, cmor_logs: Iterator, variable: str) -> str:
    """Checks the cmor log file for any additional information on cmor.axis errors for a single critical issue.

    Parameters
    ----------
    msg: str
        The current error message.
    cmor_logs: Iterator
        The content of the cmor log file as an iterator.
    variable: str
        The variable associated with the error.

    Returns
    -------
    str
        The error message updated with additional info from the cmor file.
    """
    for line in cmor_logs:
        if "cmor_axis" in line:
            return _summarise_cmor_error(line, cmor_logs, "Error", variable, "Problem with cmor_axis")

    return msg


def check_issues_for_variable(msg: str, cmor_logs: Iterator, variable: str) -> str:
    """Checks the cmor log file for any additional information where the variables are explicitly mentioned.

    Parameters
    ----------
    msg: str
        The current error message.
    cmor_logs: Iterator
        The content of the cmor log file as an iterator.
    variable: str
        The variable associated with the error.

    Returns
    -------
    str
        The error message updated with additional info from the cmor file.
    """
    for item in cmor_logs:
        if variable in item:
            if "Error" or "Warning" in item:
                return msg + ": " + item[:200].strip("! Error: ") + "..."

    return msg


def get_detail_from_cmor_logs(issue: str, cdds_convert_proc_dir: str):
    """Applies extra detail to a single critical issue if the issue references a cmor error.

    Parameters
    ----------
    issue: str
        The key information for a single critical issue.
    cdds_convert_proc_dir: str
        The path to the cdds convert proc directory.

    Returns
    -------
    str
        The new/updated error message.
    """
    cmor_log_file_location = get_cmor_log_file_location(issue, cdds_convert_proc_dir)
    msg = issue.split("|")[-1]
    if "Problem with 'cmor" in msg:
        with gzip.open(cmor_log_file_location, "r") as infile:
            cmor_logs = iter([item.strip() for item in infile])
            variable = issue.split("|")[3].split("_")[0]
            if "Problem with 'cmor.write'" in msg:
                msg = check_issues_in_cmor_write(msg, cmor_logs, variable)
            elif "Problem with 'cmor.variable'" in msg:
                msg = check_issues_in_cmor_variable(msg, cmor_logs, variable)
            elif "Problem with 'cmor.zfactor'" in msg:
                msg = check_issues_in_cmor_zfactor(msg, cmor_logs, variable)
            elif "Problem with 'cmor.axis'" in msg:
                msg = check_issues_in_cmor_axis(msg, cmor_logs, variable)
            else:
                check_issues_for_variable(msg, cmor_logs, variable)

    return msg


def calc_num_cycles(critical_issues: list) -> int:
    """Calculates the number of cycle points across the workflow.

    Parameters
    ----------
    critical_issues: list
        The list of key information about all critical issues in the file where each item is the key info for a new
        critical issue.

    Returns
    -------
    int
        The number of cycle points in the workflow.
    """
    cycle_points = set()
    for item in critical_issues:
        cycle_points.add(item.split("|")[1])

    return len(cycle_points)


def calc_num_occurrences(critical_issues_key_info: list, search_line: str) -> int:
    """Calculates the number of instances of a single critical issue over all cycle points.

    Parameters
    ----------
    critical_issues_key_info: list
        The key information about each critical issue where each item in the list is the key information of a new
        critical issue.
    search_line: str
        The error that is being counted.

    Returns
    -------
    int
        The number of occurrences of a single critical issue across all cycle points.
    """
    occurrences = 0
    for issue in critical_issues_key_info:
        issue = issue.split("|")[3:]
        if issue == search_line.split("|")[3:]:
            occurrences += 1

    return occurrences


def summarise_critical_issues(critical_issues_key_info: list, cdds_convert_proc_dir: str, num_cycles: int) -> set:
    """Summarises each critical issue into a single string noting the variable affected, its realm, the error triggered
    and how many cycles the error occurred in. we would expect that if the error occurs in one cycle then it should
    occur in all cycles. However this isn't always the case and it this does occur it is very important information to
    have available during the debugging process.

    Parameters
    ----------
    critical_issues_key_info: list
        The key information about each critical issue where each item in the list is the key information of a new
        critical issue.
    cdds_convert_proc_dir: str
        The path to the cdds convert proc directory.
    num_cycles: int
        The number of cylce points in the workflow.

    Returns
    -------
    set
        A set of summarised critical issues quoting the variable affected, its realm, the error triggered and how many
        cycles the error occurred in.
    """
    summarised_issues = set()
    for issue in critical_issues_key_info:
        num_occurrences = calc_num_occurrences(critical_issues_key_info, issue)
        _, _, _, variable, realm, msg = issue.split("|")
        msg = get_detail_from_cmor_logs(issue, cdds_convert_proc_dir)
        if num_occurrences > num_cycles:
            num_occurrences = num_cycles
        summarised_issues.add(f"'{variable}' for '{realm}' could not be produced due the error '{msg}' occuring in "
                              f"{num_occurrences} of {num_cycles} cycles")

    return summarised_issues
