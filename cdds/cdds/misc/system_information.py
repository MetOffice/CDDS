#!/usr/bin/env python3
# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import os


def check_environment_variables():
    """
    Print current values of the required environment variables.
    Notify user of any that are currently unset or any invalid paths that have been assigned.
    """
    required_vars = [
        'CYLC_VERSION',
        'TZ',
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

    for var in required_vars:
        x = env_vars.get(var)
        print(f"{var}: {x}")
        if not x:
            unset_vars.append(var)

    # Check variables with required paths are valid.
    for var in required_path_vars:
        value = env_vars.get(var)
        # If path var is unset, continue to avoid path expansion error.
        if not value:
            continue
        # Expand and validate path environment variables.
        expanded_value = os.path.expandvars(value)
        if expanded_value.startswith('source '):
            expanded_value = expanded_value[len('source '):].strip()
        if not os.path.exists(expanded_value):
            unresolved_paths.append(var)

    if unset_vars or unresolved_paths:
        print("\nIssues detected with environment variables:")
        for x in unset_vars:
            print(f"Required environment variable '{x}' is not set.")
        for x in unresolved_paths:
            print(f"Filepath for environment variable '{x}' is invalid.")

    if unset_vars or unresolved_paths:
        exit_code = 1

    else:
        exit_code = 0

    return exit_code
