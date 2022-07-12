# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for coding standards and copyright headers.
"""
import datetime
import os
import pep8
import re
import subprocess
import unittest
from nose.plugins.attrib import attr

import cdds_prepare

CHECK_LICENSE_HEADERS = False


@attr('style')
class TestCodingStandards(unittest.TestCase):
    """
    Tests for coding standards.
    """

    def setUp(self):
        cdds_prepare_dir = os.path.dirname(cdds_prepare.__file__)
        self.all_files = [
            os.path.join(dirpath, filename) for dirpath, _, filenames in
            os.walk(cdds_prepare_dir) for filename in filenames]
        self.exclude_patterns = ['conf.py', '.json', '.csv', '.css']

    def test_pep8_conformance(self):
        # Only run the PEP8 test on *.py files.
        py_files = [
            filename for filename in self.all_files if
            filename.endswith('.py') and True not in set(
                [exclude_pattern in filename for
                 exclude_pattern in self.exclude_patterns])]
        pep8style = pep8.StyleGuide(quiet=False)
        # Set the maximum line length to 120.
        pep8style.options.max_line_length = 120
        # Ignore 'line break occurred before a binary operator'.
        pep8style.options.ignore = 'W503'
        result = pep8style.check_files(py_files)
        self.assertEqual(result.total_errors, 0,
                         'Found code style errors (and warnings)')

    def test_copyright_headers(self):
        copyright_template = (
            '{start_comment} (C) British Crown Copyright {years}, Met Office.'
            '\n{start_comment} Please see LICENSE.rst for license details.')
        # Add optional shebang.
        copyright_format = r'((\#\!.*)\n)?' + re.escape(copyright_template)
        copyright_format = copyright_format.replace(r'\{start_comment\}',
                                                    r'(\#|\.{2})')
        copyright_format = copyright_format.replace(r'\{years\}', r'(.*?)')
        copyright_pattern = re.compile(copyright_format)

        # Run the copyright test on all files except those listed
        # below.
        self.exclude_patterns.extend(
            ['egg-info', 'EGG-INFO', 'dist', '.pyc', 'doctrees', 'html',
             'pylintrc', 'TAGS', 'Makefile', '.json'])
        copyright_files = [
            filename for filename in self.all_files if True not in set(
                [exclude_pattern in filename for
                 exclude_pattern in self.exclude_patterns])]

        if not CHECK_LICENSE_HEADERS:
            return
        matched = True
        for full_path in copyright_files:
            match = None
            with open(full_path, 'r') as fh:
                match = copyright_pattern.match(fh.read())
            if not match:
                matched = False
                print(('{full_path}: Missing or incorrect formatting of '
                       'copyright notice'.format(full_path=full_path)))
            # last edit date check
            last_changed_date = _get_svn_last_changed_date(full_path)
            if last_changed_date is None:
                continue
            if str(last_changed_date.year) not in match.group(4):
                print(('{0}: Year in copyright notice is inconsistent with '
                       'svn history').format(full_path))
                matched = False
        self.assertTrue(matched, 'There were license header failures')


def _run_command(cmd, ignore_fails=True):
    """
    Run the supplied command and fail with an exception if ignore_fails
    is set to False, otherwise return None.

    Parameters
    ----------
    cmd : list of str
        Command to be run by subprocess
    ignore_fails: bool
        Do not raise exception if True


    Returns
    -------
    str
        standard output from the command

    Raises
    ------
    SystemError
        If command returns a non-zero error code and ignore_fails is
        False.
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        if not ignore_fails:
            raise SystemError(('Command "{}" failed.\n stdout: {}\n stderr: {}'
                               '').format(' '.join(cmd), stdout, stderr))
        else:
            stdout = None
    return stdout


def _get_svn_last_changed_date(filename):
    """
    Use the svn command to identify when the file was last changed.

    Parameters
    ----------
    filename : str
        file to obtain last changed date for

    Returns
    -------
    datetime.datetime
        datetime of last change
    """
    date_pattern = r'Last Changed Date: (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)'
    cmd = ['svn', 'info', filename]
    output = _run_command(cmd)
    if output is None:
        return None
    last_edit_date = re.search(date_pattern, output).groups()[0]
    return datetime.datetime.strptime(last_edit_date, '%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    unittest.main()
