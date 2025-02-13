# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.md for license details.
"""
Common routines for running mip_convert_wrapper
"""
import os


def print_env():
    """
    Return a string description of the environment variables (useful
    for debugging).

    Returns
    -------
    str
       Description of the current environment variables.
    """
    output = 'environment:\n'
    for env_var in sorted(os.environ.keys()):
        output += '    "{}" : "{}"\n'.format(env_var, os.environ[env_var])
    return output
