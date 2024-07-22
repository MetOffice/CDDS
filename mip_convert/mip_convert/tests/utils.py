# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.
import os.path

import unittest

TYPE_MAP = {'CMIP5_da': 'mip'}


def _fileType(yfile):
    if yfile in TYPE_MAP:
        result = TYPE_MAP[yfile]
    else:
        (_, ext) = os.path.splitext(yfile)
        result = ext[1:]
    return result


def getTestFileBase():
    '''
    returns the path to the directory containing test files
    '''
    return os.path.join(os.environ['CDDS_ETC'], 'testdata', 'mip_table_tests')


def getTestPath(yfile):
    '''
    returns the full path for test file yfile
    '''
    return os.path.join(getTestFileBase(), _fileType(yfile), yfile)


def check_db_access():
    """
    Raises a SkipTest error if the credentials file isn't found or
    a RuntimeError if found, but doesn't have the appropriate
    permissions.
    """
    credentials_file = os.path.join(os.environ['HOME'],
                                    '.cdds_credentials')
    if os.path.exists(credentials_file):
        unix_permissions = oct(os.stat(credentials_file).st_mode)[-3:]
        if unix_permissions[1:] != '00':
            raise RuntimeError(
                'Unix permissions on "{}" must only allow owner access'
                ''.format(credentials_file))
    else:
        raise unittest.SkipTest('CDDS Credentials file "{}" not found'
                                ''.format(credentials_file))
