# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
