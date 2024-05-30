# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Common functions for tests.
"""
import subprocess
from collections import defaultdict
from cdds.tests.test_common.common import handle_process


def break_netcdf_file(filepath, nbytes=5):
    """
    Remove nbytes from the end of the specified file

    Parameters
    ----------
    filepath : str
        Path to the input file
    nbytes : int
        Number of bytes to be trunkated
    """
    command = ['truncate', '-s', '-{}'.format(nbytes), filepath]
    truncate_proc = subprocess.Popen(command, universal_newlines=True)
    handle_process(truncate_proc, command)


def init_defaultdict(init_list):
    """
    Populates defaultdict with a list of keys and ones

    Parameters
    ----------
    init_list : list
        A list of keys

    Returns
    -------
    : collections.defaultdict
        Populated dictionary
    """
    ret_dict = defaultdict(int)
    for i in init_list:
        ret_dict[i] += 1
    return ret_dict
