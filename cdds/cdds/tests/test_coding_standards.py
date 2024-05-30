# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for coding standards and copyright headers.
"""
import os
import re
import unittest
import pytest
from pathlib import Path

import pycodestyle

import cdds

COPYRIGHT_TEMPLATE = ('{start_comment} THIS FILE IS PART OF CDDS'
                      '\n{start_comment} Copyright (C) British Crown (Met Office) & Contributors.'
                      '\n{start_comment} Licenced under the BSD 3 clause license '
                      'https://opensource.org/license/bsd-3-clause'
                      '\n{start_comment} See the LICENSE file in the top level of this repository for full details.')


@pytest.mark.style
class TestCodingStandards(unittest.TestCase):
    """
    Tests for coding standards.
    """

    def setUp(self):
        cdds_dir = Path(cdds.__file__).parent.absolute()
        self.all_files = [
            os.path.join(dir, filename) for dir, _, filenames in os.walk(cdds_dir) for filename in filenames
        ]
        self.exclude_patterns = ['conf.py']

    def test_pycodestyle_conformance(self):
        # Only run the PEP8 test on *.py files.
        py_files = [
            filename for filename in self.all_files if
            filename.endswith('.py') and True not in set(
                [exclude_pattern in filename for exclude_pattern in self.exclude_patterns]
            )
        ]

        pycodestyle_guide = pycodestyle.StyleGuide(quiet=False)
        # Set the maximum line length to 120.
        pycodestyle_guide.options.max_line_length = 120
        # Ignore W503 "line break before binary operator" error
        pycodestyle_guide.options.ignore = tuple(['W503'])
        result = pycodestyle_guide.check_files(py_files)
        self.assertEqual(result.total_errors, 0, 'Found code style errors (and warnings)')

    def test_copyright_headers(self):
        # Add optional shebang.
        copyright_format = r'((\#\!.*)\n)?' + re.escape(COPYRIGHT_TEMPLATE)
        copyright_format = copyright_format.replace(r'\{start_comment\}', r'(\#|\.{2}|\-{2})')
        copyright_pattern = re.compile(copyright_format)

        copyright_files = self.get_copyright_files()
        matched = True
        for full_path in copyright_files:
            match = None
            with open(full_path, 'r') as file_handler:
                match = copyright_pattern.match(file_handler.read())
            if not match:
                matched = False
                print(('{full_path}: Missing or incorrect formatting of copyright notice'.format(full_path=full_path)))
        self.assertTrue(matched, 'There were license header failures')

    def get_copyright_files(self):
        self.exclude_patterns.extend(
            ['egg-info', 'EGG-INFO', 'dist', '.pyc', 'doctrees', 'html', 'cfg',
             'pylintrc', 'TAGS', 'json', 'todel', 'nfsc', 'txt', 'ini']
        )

        return [
            filename for filename in self.all_files if True not in set(
                [exclude_pattern in filename for exclude_pattern in self.exclude_patterns]
            )
        ]

    def get_py_files(self):
        return [
            filename for filename in self.all_files if
            filename.endswith('.py') and True not in set(
                [exclude_pattern in filename for exclude_pattern in self.exclude_patterns]
            )
        ]


if __name__ == '__main__':
    unittest.main()
