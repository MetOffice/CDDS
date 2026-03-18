# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import argparse
import logging

from cdds.common import configure_logger
from cdds.common.request.request import read_request
from cdds.common.cdds_files.cdds_directories import component_directory
from cdds.critical_check.process_critical_errors import (read_critical_log_file,
                                                         process_critical_issues,
                                                         calc_num_cycles,
                                                         summarise_critical_issues)


def parse_cdds_critical_check_command_line(user_arguments):

    parser = argparse.ArgumentParser(description='Check output logs for critical errors.')
    parser.add_argument('request', help='The full path to the cfg file containing the information from the request.')
    arguments = parser.parse_args(user_arguments)

    return arguments


def main_cdds_critical_check(arguments=None):
    args = parse_cdds_critical_check_command_line(arguments)
    request = read_request(args.request)

    configure_logger("cdds_critical_check", request.common.log_level, False)
    logger = logging.getLogger(__name__)

    cdds_convert_proc_dir = component_directory(request, 'convert')

    for stream in request.data.streams:
        logger.info(f"Checking critical erros for stream {stream}...")
        critical_issues = read_critical_log_file(cdds_convert_proc_dir, stream)
        critical_issues_key_info = process_critical_issues(critical_issues)
        num_cycles = calc_num_cycles(critical_issues)
        summary_list = summarise_critical_issues(critical_issues_key_info, cdds_convert_proc_dir, num_cycles)

        summary_set = set(summary_list)
        for line in summary_set:
            logger.info(line)
