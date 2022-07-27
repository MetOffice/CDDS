#!/usr/bin/env python3.8
# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
"""
A helper script for data volume management. Will report sizes, ages and owners of particular simulations sitting in
/project/cdds_data directory.
"""

import argparse
import math
import os
import subprocess

from datetime import datetime
from os import stat
from pwd import getpwuid

DATA_DIR = '/project/cdds_data/CMIP6/'


def scan_datadir(root):
    """
    Builds a inventory of datasets at provided location

    Parameters
    ----------
    root: str
        Root of the data directory.

    Returns
    -------
    : list
        A list of tuples in the form (file size, human-readable size, dataset path, modification date, owner)
    """
    rval = []

    def do_scan(start_dir,output,depth=0, threshold=1e6):
        for f in os.listdir(start_dir):
            ff = os.path.join(start_dir,f)
            if os.path.isdir(ff):
                if depth<4:
                    do_scan(ff,output,depth+1)
                else:
                    (size, dirpath, modified, user) = dir_info(ff)
                    if size >= threshold:
                        output.append((size, make_human_readable(float(size)), dirpath, modified, user))
    do_scan(root,rval,0)
    return rval


def find_owner(filepath):
    """
    Username of file's owner.

    Parameters
    ----------
    filepath: str
        Filepath.

    Returns
    -------
    : str
        Username.
    """
    return getpwuid(stat(filepath).st_uid).pw_name


def dir_info(dirpath):
    """
    Gets information about the size, last modification date and owner of the provided directory.

    Parameters
    ----------
    dirpath: str
        Path to the directory.
    Returns
    -------
    : tuple
        Directory data in the form of (size, path, last modification date, username)
    """

    p = subprocess.Popen(['du', '-s',  '--apparent-size', dirpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if not err:
        size, dirpath = out.split()
        modified = datetime.fromtimestamp(os.path.getmtime(dirpath))
        user = find_owner(dirpath)
        return int(size), dirpath, modified, user
    else:
        print(err)


def make_human_readable(value):
    """
    Converts size in kilobytes to human-readable form.

    Parameters
    ----------
    value: int
        Size in kb

    Returns
    -------
    : str
        Size in human-readable form (e.g. 12.4G)
    """
    exponent = math.log10(value)
    if exponent < 3:
        suffix = 'K'
        denominator = 1.0
    elif exponent < 6:
        suffix = 'M'
        denominator = 1e3
    elif exponent < 9:
        suffix = 'G'
        denominator = 1e6
    elif exponent < 12:
        suffix = 'T'
        denominator = 1e9
    return '{}{}'.format(round(value/denominator, 2), suffix)


def get_largest(inventory, threshold=100e6, days=30):
    """
    Filters inventory to get files larger and older than provided thresholds.

    Parameters
    ----------
    inventory: list
        Dataset inventory.

    threshold: int|float
        Size threshold in kilobytes, default is 100 gigabytes (100e6).
    days:
        Age threshold.
    Returns
    -------
    : list
        Filtered dataset list.
    """
    result = []
    for i in inventory:
        if i[0] >= threshold and (datetime.now() - i[3]).days > days:
            result.append(i)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', default=100e9, help='Reporting size threshold')
    parser.add_argument('--age', default=30, help='Reporting age threshold')
    parser.add_argument('filename', help='Report filename')

    args = parser.parse_args()
    inventory = scan_datadir(DATA_DIR)
    threshold_in_KB = int(args.threshold)/1000.0
    sorted = sorted(inventory, key=lambda k: k[0])[::-1]
    with open(args.filename, "w") as fp:
        fp.write('DATASETS LARGER THAN {} AND OLDER THAN {} DAYS:\n'.format(make_human_readable(threshold_in_KB), args.age))
        fp.write('size\t\tfilepath\tlast modified\towner\n')
        for j in get_largest(sorted, threshold_in_KB, args.age):
            fp.write('{}\t\t{}\t{}\t{}\n'.format(j[1], j[2], j[3].isoformat(), j[4]))
        fp.write('\nFULL REPORT:\n')
        fp.write('size\t\tfilepath\tlast modified\towner\n')
        for i in sorted:
            fp.write('{}\t\t{}\t{}\t{}\n'.format(i[1], i[2], i[3].isoformat(), i[4]))
