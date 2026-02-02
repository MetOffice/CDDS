# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

from pathlib import Path
import gzip
import csv

CONVERT_LOG_DIR = Path('demonstrator/ukcm2_test/round_2/proc/convert/log')
CONVERT_CRITICAL_LOG_FILE_LOCATION = CONVERT_LOG_DIR / "critical_issues.log"


def read_critical_logs(path: Path):
    with open(path, "r") as fh:
        critical_logs = [line.strip() for line in fh]

    return critical_logs


def get_variable_from_critical_logs(error_msg: str):
    variable = error_msg.split("CRITICAL:")[1].split('"')[1]
    shortened_variable = variable.split("_")[0]

    return variable, shortened_variable


def get_realm_from_critical_logs(error_msg: str):

    return error_msg.split("CRITICAL:")[1].split('"')[3]


def get_condensed_message_from_critical_logs(error_msg: str):

    return error_msg.split("CRITICAL:")[1].split(':')[1]


def get_cmor_log_file_location(grid: str, mip_log_file: str, timestamp: str):
    subdir = "_".join(grid.split("_")[2:])
    subdir = "ap4_atmos-native" if subdir == "first_ap4_atmos-native" else subdir
    subdir = "ap5_atmos-native" if subdir == "first_ap5_atmos-native" else subdir
    cmor_log_filename = f'{mip_log_file.replace("mip_convert_", "cmor.")}.gz'
    cmor_log_file_location = CONVERT_LOG_DIR / subdir / timestamp / "cmor_logs" / cmor_log_filename

    return cmor_log_file_location


def check_issues_in_cmor_write(msg, cmor_logs, additional_info):
    if "Problem with 'cmor.write'" in msg:
        for item in cmor_logs:
            if b"cmor_write_var_to_file" in item:
                snippet = [item, next(cmor_logs), next(cmor_logs), next(cmor_logs), next(cmor_logs),
                        next(cmor_logs)]
                for text in snippet:
                    if b"Error" in text:
                        additional_info.add(text.strip(b"b'! "))


def check_issues_in_cmor_variable(msg, cmor_logs, shortened_variable, additional_info):
    if "Problem with 'cmor.variable'" in msg:
        for item in cmor_logs:
            if b"cmor_variable" in item:
                snippet = [item, next(cmor_logs), next(cmor_logs), next(cmor_logs), next(cmor_logs),
                        next(cmor_logs)]
                for text in snippet:
                    if b"Error" in text and shortened_variable.encode() in text:
                        additional_info.add(text.strip(b"b'! "))


def check_issues_in_cmor_zfactor(msg, cmor_logs, additional_info):
    if "Problem with 'cmor.zfactor'" in msg:
        for item in cmor_logs:
            if b"cmor_zfactor" in item:
                snippet = [item, next(cmor_logs), next(cmor_logs), next(cmor_logs), next(cmor_logs),
                        next(cmor_logs)]
                for text in snippet:
                    if b"Error" in text:
                        additional_info.add(text.strip(b"b'! "))


def check_issues_in_cmor_axis(msg, cmor_logs, additional_info):
    if "Problem with 'cmor.axis'" in msg:
        for item in cmor_logs:
            if b"cmor_axis" in item:
                snippet = [item, next(cmor_logs), next(cmor_logs), next(cmor_logs), next(cmor_logs),
                        next(cmor_logs)]
                for text in snippet:
                    if b"Error" in text:
                        additional_info.add(text.strip(b"b'! "))


def build_information_dict(grid, realm, variable, mip_log_file, msg, additional_info):

    return {
        "grid": grid,
        "realm": realm,
        "variable": variable,
        "mip_log_file": mip_log_file,
        "error_msg": msg.strip(),
        "additional_info": additional_info
    }


def write_error_info_to_csv(outfile: Path, error_info):
    with open(outfile, 'w', newline='') as csvfile:
        fieldnames = ['grid', 'realm', 'variable', 'mip_log_file', "error_msg", "additional_info"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(error_info)
        print(f"File saved as {outfile}")


def main():
    critical_logs = read_critical_logs(CONVERT_CRITICAL_LOG_FILE_LOCATION)
    error_info = []

    for line in critical_logs:
        additional_info = set()

        grid, timestamp, _, mip_log_file, error_msg = line.split("|")
        variable, shortened_variable = get_variable_from_critical_logs(error_msg)
        realm = get_realm_from_critical_logs(error_msg)
        msg = get_condensed_message_from_critical_logs(error_msg)

        cmor_log_file_location = get_cmor_log_file_location(grid, mip_log_file, timestamp)
        if "Problem with 'cmor" in msg:
            with gzip.open(cmor_log_file_location, "rb") as infile:
                cmor_logs = iter([item.strip() for item in infile])
                check_issues_in_cmor_write(msg, cmor_logs, additional_info)
                check_issues_in_cmor_variable(msg, cmor_logs, shortened_variable, additional_info)
                check_issues_in_cmor_zfactor(msg, cmor_logs, additional_info)
                check_issues_in_cmor_axis(msg, cmor_logs, additional_info)
                for item in cmor_logs:
                    if b"Error" in item and shortened_variable.encode() in item:
                        additional_info.add(item.strip(b"b'! "))

        data = build_information_dict(grid, realm, variable, mip_log_file, msg, additional_info)
        error_info.append(data)

    write_error_info_to_csv(CONVERT_LOG_DIR / "ukcm2_critical_errors.csv", error_info)


if __name__ == "__main__":
    main()
