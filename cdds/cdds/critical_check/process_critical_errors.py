# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

import os


def read_critical_log_file(mip_convert_config_dir, stream):
    logfile = os.path.join(mip_convert_config_dir, "log", f'critical_issues_{stream}.log')
    with open(logfile, "r") as critical_logs:
        critical_issues = critical_logs.readlines()

    return critical_issues


def process_critical_issues(critical_issues: list):
    critical_issues_key_info = []
    for item in critical_issues:
        info = "".join(item.split("|")[-1].split(":")[3:])
        variable = info.split('"')[1]
        realm = info.split('"')[3]
        msg = '"'.join(info.split('"')[4:])
        critical_issues_key_info.append(f"{variable}|{realm}|{msg.strip()}")

    return critical_issues_key_info


def calc_num_cycles(critical_issues: list):
    cycle_points = set()
    for item in critical_issues:
        cycle_points.add(item.split("|")[1])

    return len(cycle_points)


def summarise_critical_issues(critical_issues_key_info, num_cycles):
    summarised_issues = set()
    for issue in critical_issues_key_info:
        num_occurances = critical_issues_key_info.count(issue)
        variable, realm, msg = issue.split("|")
        if num_occurances > num_cycles:
            num_occurances = num_cycles
        summarised_issues.add(f"'{variable}' for '{realm}' could not be produced due the error '{msg}' occuring in "
                              f"{num_occurances} of {num_cycles} cycles")

    return summarised_issues
