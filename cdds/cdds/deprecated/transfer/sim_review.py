# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`sim_review` module contains code to extract information to facilitate reviewing whether simulation tickets
have been correctly processed before the data is submitted for publication.
"""
import datetime
import logging
import os
import subprocess

from cdds.common.constants import COMPONENT_LIST, APPROVED_VARS_DATETIME_STREAM_REGEX, APPROVED_VARS_FILENAME_TEMPLATE
from cdds.common.io import read_json
from cdds.common import get_most_recent_file_by_stream
from cdds.common.request.request import Request
from cdds.common.plugins.plugins import PluginStore


def filter_critical_issues(issue_list: list[str]) -> set[list[str]]:
    """Filters reported issues by removing the prefix from the string, to show only the actual error message, and
    consolidate and sort error messages to remove repeats.

    Parameters
    ----------
    issue_list: list[str]
        A list of string from a critical error log.

    Returns
    -------
    list[str]
        A filtered list of critical error strings.
    """
    filtered_issues = []
    for issue_str in issue_list:
        try:
            filtered_issues += [' '.join(issue_str.split(' ')[4:])]
        except IndexError:
            filtered_issues += [issue_str]

    return sorted(set(filtered_issues))


def remove_empty_list_elements(output_list: list[str]) -> list[str]:
    """Removes any blank elements from a single list. The nature of using .split('\n') on the subprocess output causes
    an empty element to be appended at the end of the output leading to unnecessary blank lines within the logs.

    Parameters
    ----------
    output_list: list[str]
        The list of outputs from the subprocess command.

    Returns
    -------
    list[str]
        The list of outputs from the subprocess command with no empty elements.
    """
    for line in output_list:
        if not line:
            output_list.remove(line)

    return output_list


def check_critical_issues(proc_dir: str) -> None:
    """Look for critical issues in the component proc directories. This function also checks for errors in transfer for
    legacy reasons, and for the presence of a critical_isues.log file in the convert proc dir, which is where
    mip_convert critical issues are reported.

    Parameters
    ----------
    proc_dir: str
        Path to the proc directory for this package.
    """
    logger = logging.getLogger(__name__)
    logger.info('Checking for critical issues in CDDS components.')
    for component in COMPONENT_LIST:
        package_dir = os.path.join(proc_dir, component)
        cmd1 = ['grep', '-irI', 'critical', package_dir, '--exclude', '*.py', '--exclude', '*.svn*']
        try:
            output = subprocess.check_output(cmd1, universal_newlines=True)
            output_lines = remove_empty_list_elements(output.split('\n'))
            compact_output = '\n'.join(filter_critical_issues(output_lines))
            logger.info('Critical issues in {0}:'.format(component))
            logger.info(compact_output)
        except subprocess.CalledProcessError as e1:
            # If the return code is 1, then no critical issues were found.
            if e1.returncode == 1:
                logger.info('No critical issues in {0}.'.format(component))
            else:
                logger.exception(e1)
        except RuntimeError as e1:
            logger.exception(e1)

    convert_critical_issues_path = os.path.join(proc_dir, 'convert', 'critical_issues.log')
    if os.path.isfile(convert_critical_issues_path):
        with open(convert_critical_issues_path) as ccif:
            raw_issues = ccif.readlines()
            convert_critical_issues = filter_critical_issues(raw_issues)
            cci_msg_str = '\n'.join(convert_critical_issues)

        msg = (
            'Critical issues found for CDDS convert. '
            'Contents of file {0}:\n{1}'.format(convert_critical_issues_path, cci_msg_str))
        logger.info(msg)
    else:
        logger.info('No convert critical issues log file found.')


def check_intermediate_files(data_dir: str) -> None:
    """Check whether the  intermediate directories in the data output directory (directories with the suffix
    _mip_convert or _concat), have any remaining files in them or subdirectories. If there are this usually indicates a
    convert task has failed or not run.

    Parameters
    ----------
    data_dir: str
        Path to the data directory for this package.

    Raises
    ------
    RuntimeError:
        If partial files are found in the output directories.
    """
    logger = logging.getLogger(__name__)
    logger.info('Checking for intermediate files in output directories.')
    output_dir = os.path.join(data_dir, 'output')
    inter_dirs = [os.path.join(output_dir, dir1) for dir1 in
                  os.listdir(output_dir) if
                  '_concat' in dir1 or '_mip_convert' in dir1]
    inter_dirs_clean = True
    for id1 in inter_dirs:
        partial_files_found = any(len(files) != 0 for path1, dirs, files in os.walk(id1))
        if partial_files_found:
            err_msg = ('Partial files found in intermediate directory:\n{0}\n'
                       'Please check that all convert tasks completed successfully'.format(id1))
            inter_dirs_clean = False
            logger.error(err_msg)
    if inter_dirs_clean:
        logger.info('No intermediate convert files found.')
    else:
        msg = 'Partial files found, please check convert tasks.'
        logger.critical(msg)
        raise RuntimeError(msg)


def check_qc_report(qc_dir: str) -> None:
    """Check whether there are any issues reported in the most recent QC report file.

    Parameters
    ----------
    qc_dir: str
        Path to the `qualitycheck` proc directory for this package.
    """
    logger = logging.getLogger(__name__)
    logger.info('Checking QC report.')
    prefix = 'report'
    # Note that the report file name uses a similar format to the approved vars file, hence the use of the approved
    # variables regex
    report_name_regex_str = prefix + '_' + APPROVED_VARS_DATETIME_STREAM_REGEX + '\\.json'
    reports_dict = get_most_recent_file_by_stream(qc_dir, prefix, report_name_regex_str)
    # Loop over each report and flag up issues if there are items in the QC reports
    for report_path in reports_dict.values():
        logger.info('Reading QC report "{0}"'.format(report_path))

        report = read_json(report_path)

        for section in ['aggregated_summary', 'details']:
            if report[section] == []:
                logger.info('Nothing reported in {0} in QC report.'.format(section))
            else:
                msg = ('Problems reported in {0} of report {1}, please investigate further.'.format(section,
                                                                                                    report_path))
                logger.critical(msg)


def display_approved_variables(qc_dir: str) -> str:
    """Open the approved variables file in an editor for the reviewer to check manually. The editor used is defined by
    the $EDITOR environment variable. If this is not set, the user is prompted to open the file manually and the path
    specified in the log.

    Parameters
    ----------
    qc_dir: str
        Path to the `qualitycheck` proc directory for this package.

    Returns
    -------
    str
        The path to the most recent approved variables list.
    """
    logger = logging.getLogger(__name__)
    logger.info('Opening approved variables files.')
    approved_prefix = 'approved_variables'
    approved_regex = approved_prefix + '_' + APPROVED_VARS_DATETIME_STREAM_REGEX + '\\.txt'

    recent_approved_path_dict = get_most_recent_file_by_stream(qc_dir, approved_prefix, approved_regex)
    # If there is an aggregated approved variables file (or qc was run for a whole package use that file, otherwise
    # amalgamate the per stream approved variables files.
    if None in recent_approved_path_dict:
        recent_approved_path_file = recent_approved_path_dict[None]
        logger.info('Found whole package approved variables file: "{}"'.format(recent_approved_path_file))
    else:
        recent_approved_path_file = _join_approved_files(recent_approved_path_dict)

    # Append the approved variable file to the logs
    with open(recent_approved_path_file, "r") as fh:
        approved_variables = remove_empty_list_elements(fh.read().split('\n'))
        approved_variable_output = '\n'.join(approved_variables)
        logger.info("-----")
        logger.info(approved_variable_output)
        logger.info("-----")

    return recent_approved_path_file


def _join_approved_files(path_file_dict):
    logger = logging.getLogger(__name__)
    per_stream_files = list(path_file_dict.values())
    if not per_stream_files:
        logger.critical("No approved variable files could be found. This likely means that either qc has not run or "
                        "nothing was produced.")
    datetime_suffix = str(datetime.datetime.now().replace(microsecond=0).isoformat()).replace(":", "")
    combined_file = APPROVED_VARS_FILENAME_TEMPLATE.format(dt=datetime_suffix)
    combined_file_path = os.path.join(os.path.dirname(per_stream_files[0]), combined_file)
    # Join the per stream files together and write out under current date stamp
    with open(combined_file_path, 'w') as combined_fh:
        for stream_file in per_stream_files:
            with open(stream_file, 'r') as stream_fh:
                combined_fh.write(stream_fh.read())

    return combined_file_path


def show_submission_command(request_file_path: str, recent_approved_path: str) -> None:
    """Constructs and displays scp commands to be used by the reviewer to copy the files needed by the move_in_mass
    command to the server where the command can be run.

    Parameters
    ----------
    request_file_path: str
        Path to the request configuration for this package.
    recent_approved_path: str
        The path to the most recent approved variables list.
    """
    logger = logging.getLogger(__name__)
    logger.info('Command for data submission:')
    logger.info('move_in_mass {request} -o . \\\n--original_state=embargoed --new_state=available '
                '\\\n--approved_variables_path={recent_approved_path}'
                ''.format(request=request_file_path, recent_approved_path=recent_approved_path))


def do_sim_review(request: Request, request_file_path: str) -> None:
    """The main work function for the simulation review script.

    Parameters
    ----------
    request: Request
        The request configuration to consider
    request_file_path: str
        Path to the given request configuration file

    Raises
    ------
    IOError
        If the specified proc or data directory is not a valid.
    """
    # Set up the relevant paths
    plugin = PluginStore.instance().get_plugin()
    proc_dir = plugin.proc_directory(request)
    data_dir = plugin.data_directory(request)

    if not os.path.isdir(proc_dir):
        msg = ('The specified proc dir {0} is not a valid directory, please check your arguments.'.format(proc_dir))
        raise IOError(msg)

    if not os.path.isdir(data_dir):
        msg = ('The specified data dir {0} is not a valid directory, please check your arguments.'.format(data_dir))
        raise IOError(msg)

    qc_dir = os.path.join(proc_dir, 'qualitycheck')

    check_critical_issues(proc_dir)

    check_intermediate_files(data_dir)

    check_qc_report(qc_dir)

    recent_approved_path = display_approved_variables(qc_dir)

    show_submission_command(request_file_path, recent_approved_path)
