# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
# function that iterates over env vars in turn and prints them. If any arent set  or paths dont exist it should be flagged provides 1 exit code if it fails
#put wrapper into bin
import os
import argparse
# from cdds import _DEV

def check_environment_variables():
    """
    Print current values of the required environment variables.
    Notify user of any that are currently unset or any invalid paths that have been assigned.
    """
    required_vars = [
        'CYLC_VERSION',
        'TZ'
        'CDDS_PLATFORM',
        'CDDS_ETC',
        'CDDS_ENV_COMMAND',
    ]

    required_path_vars = [
        'CDDS_ETC',
        'CDDS_ENV_COMMAND'
    ]

    env_vars = dict(os.environ)
    unset_vars = []
    unresolved_paths = []

    # Print required environment variables from environ and notify user if any are not set.
    for var in required_vars:
        x = env_vars.get(var)
        print(f"{var}: {x}")
        if x is None:
            unset_vars.append(var)
            print(f"Required environment variable '{var}' is not set.")

    # Check variables with required paths are valid.
    for var in required_path_vars:
        expanded_value = os.path.expandvars(env_vars[var])
        if expanded_value.startswith('source '):
            expanded_value = expanded_value[len('source '):].strip()
        if not os.path.exists(expanded_value):
            unresolved_paths.append(var)
            print(f"Path '{expanded_value}' for '{var}' is not valid.")

    if unset_vars or unresolved_paths:
        exit_code = 1
    
    else:
        exit_code = 0

check_environment_variables()


