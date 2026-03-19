# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

import os
import gzip
from pathlib import Path


def read_critical_log_file(mip_convert_config_dir, stream):
    logfile = os.path.join(mip_convert_config_dir, "log", f'critical_issues_{stream}.log')
    with open(logfile, "r") as critical_logs:
        critical_issues = critical_logs.readlines()

    return critical_issues


def process_critical_issues(critical_issues: list):
    critical_issues_key_info = []
    for line in critical_issues:
        grid, timestamp, round, mip_log_file, error_msg = line.split("|")
        info = "".join(error_msg.split(":")[3:])
        variable = info.split('"')[1]
        realm = info.split('"')[3]
        msg = '"'.join(info.split('"')[4:])

        critical_issues_key_info.append(f"{grid}|{timestamp}|{mip_log_file}|{variable}|{realm}|{msg.strip()}")

    return critical_issues_key_info


def get_cmor_log_file_location(critical_issues_key_info, cdds_convert_proc_dir):
    grid, timestamp, mip_log_file, _, _, _ = critical_issues_key_info.split("|")
    subdir = "_".join(grid.split("_")[2:]).strip("first_")
    cmor_log_filename = f'{mip_log_file.replace("mip_convert_", "cmor.")}.gz'
    cmor_log_file_location = Path(cdds_convert_proc_dir) / "log" / subdir / timestamp / "cmor_logs" / cmor_log_filename

    return cmor_log_file_location


def check_issues_in_cmor_write(issue, msg, cmor_logs):
    variable = issue.split("|")[3]
    for item in cmor_logs:
        if b"cmor_write_var_to_file" in item:
            snippet = [item, next(cmor_logs), next(cmor_logs), next(cmor_logs), next(cmor_logs),
                    next(cmor_logs)]
            for text in snippet:
                if b"Error" in text:
                    return msg + text.decode()[:200] + "..."


def check_issues_in_cmor_variable(issue, msg, cmor_logs):
    variable = issue.split("|")[3]
    for item in cmor_logs:
        if b"cmor_variable" in item:
            snippet = [item, next(cmor_logs), next(cmor_logs), next(cmor_logs), next(cmor_logs),
                    next(cmor_logs)]
            for text in snippet:
                if b"Error" in text and variable.split("_")[0].encode() in text:
                    return msg + text.decode()[:200] + "..."


def check_issues_in_cmor_zfactor(msg, cmor_logs):
    for item in cmor_logs:
        if b"cmor_zfactor" in item:
            snippet = [item, next(cmor_logs), next(cmor_logs), next(cmor_logs), next(cmor_logs),
                    next(cmor_logs)]
            for text in snippet:
                if b"Error" in text:
                    return msg + text.decode()[:200] + "..."


def check_issues_in_cmor_axis(msg, cmor_logs):
    for item in cmor_logs:
        if b"cmor_axis" in item:
            snippet = [item, next(cmor_logs), next(cmor_logs), next(cmor_logs), next(cmor_logs),
                    next(cmor_logs)]
            for text in snippet:
                if b"Error" in text:
                    return msg + text.decode()[:200] + "..."


def get_detail_from_cmor_logs(issue, cdds_convert_proc_dir):
    cmor_log_file_location = get_cmor_log_file_location(issue, cdds_convert_proc_dir)
    msg = issue.split("|")[-1]
    shortened_variable = issue.split("|")[3].split("_")[0]
    if "Problem with 'cmor" in msg:
        with gzip.open(cmor_log_file_location, "rb") as infile:
            cmor_logs = iter([item.strip() for item in infile])
            if "Problem with 'cmor.write'" in msg:
                msg = check_issues_in_cmor_write(issue, msg, cmor_logs)
            elif "Problem with 'cmor.variable'" in msg:
                msg = check_issues_in_cmor_variable(issue, msg, cmor_logs)
            elif "Problem with 'cmor.zfactor'" in msg:
                msg = check_issues_in_cmor_zfactor(msg, cmor_logs)
            elif "Problem with 'cmor.axis'" in msg:
                msg = check_issues_in_cmor_axis(msg, cmor_logs)
            for item in cmor_logs:
                if b"Error" in item and shortened_variable.encode() in item:
                    msg = msg + item

    return msg


def calc_num_cycles(critical_issues: list):
    cycle_points = set()
    for item in critical_issues:
        cycle_points.add(item.split("|")[1])

    return len(cycle_points)


def calc_num_occurances(critical_issues_key_info, search_line):
    occurances = 0
    for issue in critical_issues_key_info:
        issue = issue.split("|")[3:]
        if issue == search_line.split("|")[3:]:
            occurances += 1

    return occurances


def summarise_critical_issues(critical_issues_key_info, cdds_convert_proc_dir, num_cycles):
    summarised_issues = set()
    for issue in critical_issues_key_info:
        num_occurances = calc_num_occurances(critical_issues_key_info, issue)
        _, _, _, variable, realm, msg = issue.split("|")
        msg = get_detail_from_cmor_logs(issue, cdds_convert_proc_dir)
        if num_occurances > num_cycles:
            num_occurances = num_cycles
        summarised_issues.add(f"'{variable}' for '{realm}' could not be produced due the error '{msg}' occuring in "
                              f"{num_occurances} of {num_cycles} cycles")

    return summarised_issues
